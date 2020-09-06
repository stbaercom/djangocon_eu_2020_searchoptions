import time
from collections import namedtuple

from django import forms
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, F
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .elastic_helper import multi_search_facets
from .models import FTSReview

SearchResult = namedtuple("SearchResult", "docs facets num".split())


def review_detail(request, pid, uid):
    review = get_object_or_404(FTSReview, productId=pid, userId=uid)
    return render(request, 'reviews/detail.html', {'review': review})


def review_list(request):
    reviews = FTSReview.objects.all()
    paginator = Paginator(reviews, 10)  # 3 posts in each page
    page = request.GET.get('page')
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)
    return render(request, 'reviews/list.html', {'reviews': reviews, 'page': page, })


def sql_contains(qstring, qnum):
    q_summary = Q(review_summary__icontains=qstring)
    q_text = Q(review_text__icontains=qstring)
    search_query = q_summary | q_text
    reviews = FTSReview.objects.filter(
        search_query
    )
    num = reviews.count()
    return SearchResult(reviews[:qnum], {}, num)


def sql_search(qstring, qnum):
    q_summary = Q(review_summary__search=qstring)
    q_text = Q(review_text__search=qstring)
    search_query = q_summary | q_text
    reviews = FTSReview.objects.filter(
        search_query
    )
    num = reviews.count()
    return SearchResult(reviews[:qnum], {}, num)


def fts_search(qstring, qnum):
    reviews = FTSReview.objects.annotate(
        search=SearchVector('review_text', 'review_summary'),
    ).filter(
        search=qstring
    )
    num = reviews.count()
    return SearchResult(reviews[:qnum], {}, num)


def ranked_fts_search(qstring, qnum):
    search_vector = SearchVector('review_summary', weight='A') + \
                    SearchVector('review_text', weight='B')
    search_query = SearchQuery(qstring, config='english')
    reviews = FTSReview.objects.annotate(
        rank=SearchRank(search_vector, search_query)
    ).filter(rank__gte=0.3).order_by('-rank')
    num = reviews.count()
    return SearchResult(reviews[:qnum], {}, num)


def indexed_fts_search(qstring, qnum):
    search_query = SearchQuery(qstring, config='english')
    reviews = FTSReview.objects.filter(review_index=search_query)
    num = reviews.count()
    return SearchResult(reviews[:qnum], {}, num)


def ranked_indexed_fts_search(qstring, qnum):
    search_vector = F("review_index")
    search_query = SearchQuery(qstring)
    search_rank = SearchRank(search_vector, search_query)
    reviews = FTSReview.objects.annotate(rank=search_rank
                                         ).filter(rank__gte=0.05).order_by('-rank')
    num = reviews.count()
    return SearchResult(reviews[:qnum], {}, num)


def faceted_elastic_search(qstring, qnum):
    eresults = multi_search_facets("reviews", qstring, qnum)
    facets = {}

    for k, vs in eresults['aggregations'].items():
        facets[k] = {}
        for b in vs['buckets']:
            facets[k][b['key']] = b['doc_count']

    id_list = [v['_id'] for v in eresults['hits']['hits']]
    reviews = FTSReview.objects.filter(id__in=id_list)
    num = eresults['hits']['total']['value']
    return SearchResult(reviews[:qnum], facets, num)


SEARCH_METHODS = {
    'SQL Contains': sql_contains,
    "SQL Search": sql_search,
    "Simple FTS": fts_search,
    "Ranked FTS with Cutoff": ranked_fts_search,
    "Indexed Simple FTS": indexed_fts_search,
    "Indexed Ranked FTS with Cutoff": ranked_indexed_fts_search,
    "Faceted Elastic Search": faceted_elastic_search
}


class SearchForm(forms.Form):
    qnum = forms.ChoiceField(label="# of Results", choices=[(str(v), v) for v in [3, 10, 50, 100]])
    qtype = forms.ChoiceField(label="Search Types", choices=[(v, v) for v in SEARCH_METHODS.keys()])
    qstring = forms.CharField(label="Search", max_length=20)


@csrf_exempt
def search_list(request):
    form = SearchForm(request.GET)
    if form.is_valid():
        qstring = form.cleaned_data['qstring']
        method = form.cleaned_data['qtype']
        num = int(form.cleaned_data['qnum'])
        func = SEARCH_METHODS[method]
        start = time.time()
        search_results = func(qstring, num)
        end = time.time()
        diff = (end - start) * 1000.0
        diff_str = f'{diff:.5f}'
        val = {
            'form': form,
            'reviews': search_results.docs,
            'method': method,
            'diff': diff_str,
            'facets': search_results.facets,
            'num': search_results.num
        }
    else:
        val = {'form': SearchForm()}
    return render(request, 'reviews/search.html', val)

def search_list_simple(request):
    reviews = []
    method = ""
    form = SearchForm(request.GET)

    if form.is_valid():
        qstring = form.cleaned_data['qstring']
        method = form.cleaned_data['qtype']
        func = SEARCH_METHODS[method]
        reviews, facets = func(qstring)
    else:
        form = SearchForm()
    val = {
        'form': form,
        'reviews': reviews,
        'method': method,
        'facets': facets
    }
    return render(request, 'reviews/search.html', val)
