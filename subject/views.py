#django 
from .models import *
from django.shortcuts import  render
from django.views.generic import ListView, DetailView, FormView
from .forms import SubjectSearchForm
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#과목 상세페이지 NAVER API 연결 위한 모듈 
from subex.settings import CLIENT_ID, CLIENT_SECRET
import urllib.request
import json
import urllib

#과목 상세페이지 wordcloud 생성 위한 모듈
import random

#검색결과리스트, 태그포함과목리스트 tfidfv 정렬 위한 모듈 
import pandas as pd
from django_pandas.io import read_frame
from sklearn.feature_extraction.text import TfidfVectorizer
from django.db.models import Case, When

class SubjectLV(ListView):
    model=Subject
    paginate_by=10

## 과목 상세페이지 ClassBasedView
class SubjectDV(DetailView):
    model = Subject
    def get_context_data(self, **kwargs):
        context= super(SubjectDV, self).get_context_data(**kwargs)
        queryset=self.get_object()

        #상위 20개 키워드 태그로 워드 클라우드 생성
        q=str(queryset.tags)
        q=q.split(',')
        word_dict = {q[i]:i for i in range(0, len(q))}
        keys = list(word_dict.keys())
        random.shuffle(keys)  
        word_random_dict={}
        for key in keys:
            word_random_dict[key]=word_dict[key]

        context['words']=word_random_dict

        #유사강의 추천
        #sim_ids -> 해당 과목 객체의 유사과목 id리스트 
        sim_ids=list(RecommendSubject.objects.filter(subject=self.object.pk).
        values('recommend_subject').values_list('recommend_subject_id', flat=True))
        sim=[]
        for i in sim_ids:
            sim.append(Subject.objects.get(id=i))

        context['simsub']=sim
       
        # Kmooc 에서 해당 과목 pk를 subject_ids 로 갖고 있는 쿼리셋을 context에 추가
        obj= Kmooc.objects.filter(subject_ids=self.object.pk)
        context['Mooclist']=obj
        
        # 네이버 API 로 추천교재 검색. 검색 단어(query)는 강의 키워드 상위3개
        if len(queryset.keywords_3) != 0:
            query=queryset.keywords_3
            context['book_query']='단어로 검색'

        # 결과가 존재하지 않을 경우, 검색 단어(query)는 강의명
        else:
            query=queryset.name
            context['book_query']='강의명으로 검색'
        context['query']=query

        #display=3&sort=count -> 검색 결과 판매량 상위 책 3권의 데이터 json 형식으로 저장.
        client_id=CLIENT_ID
        client_secret= CLIENT_SECRET
        encText = urllib.parse.quote(query) #검색어 입력
        url = "https://openapi.naver.com/v1/search/book?query=" + encText +"&display=3&sort=count" 
        
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id",client_id)
        request.add_header("X-Naver-Client-Secret",client_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()

        if(rescode==200):
            response_body = response.read()
            json_rt=response_body.decode('utf-8')
            json_load=json.loads(json_rt)
            context['Booklist']=json_load['items'] 
            return context
        
        else:
            print("Error Code:" + rescode)
            return context

## 검색결과페이지 FunctionBasedView
def search(request):
    form=SubjectSearchForm()
    template_name='subject/resultlist.html'
    context={}

    #검색 query -> 검색단어(searchWord), 년도(Year), 학기(Semester)
    searchWord=request.GET.get('search_word')
    Year=request.GET.get('year')
    Semester=request.GET.get('semester')
    
    subject_list=Subject.objects.filter(Q(name__icontains=searchWord)|Q(professor__iexact=searchWord)|
    Q(series_num__iexact=searchWord)|Q(department__iexact=searchWord)|Q(tags__icontains=searchWord)).distinct()

    if (Year =='-') and (Semester =='-'):
        result_list=subject_list

    elif (Year !='-') and (Semester =='-'):
        result_list=subject_list.filter(Q(year=Year))
                
    elif (Year =='-') and (Semester !='-'):
        result_list=subject_list.filter(Q(semester__iexact=Semester))
    else:
        result_list=subject_list.filter(Q(year__exact=Year)& Q(semester__exact=Semester))

    #정렬 알고리즘 -> tf-idf / result_list 존재할 때 실행
    if result_list:
        #검색 결과 나온 Queryset(result_list)의 전체단어(words) 컬럼으로 tfidf 계산
        data=read_frame(result_list, fieldnames=['id', 'words'], index_col='id')
        A=data["words"].values.astype('U')
        tfidfv=TfidfVectorizer().fit(A)
        vocab_dict=tfidfv.vocabulary_
        B=tfidfv.transform(A).toarray()
        df=pd.DataFrame(B)

        #tfidfv 에서 검색단어에 해당하는 index 추출
        #검색단어가 전체단어리스트에 포함되어 있는 경우
        try: 
            id=vocab_dict[searchWord]

        #검색단어가 강의명, 교수명, 학과명이어서 전체단어리스트에 포함되어 있지 않는 경우 
        except:
            id=1

        if id!=1:
            #검색 단어 index로 가중치 내림차순 정렬(가중치가 높을수록 검색단어의 과목 내 중요도가 높음)
            df=df.sort_values(by=[id], axis=0, ascending=[False])
            #list로 저장
            sortlist=list(df.index)

        #id=1일 때는 queryset dataframe index 단순 list화
        else:
            sortlist=list(df.index)

        #sortlist -> result_list를 dataframe 화하면서 새롭게 붙여진 index로 tfidf 가중치 내림차순 정렬한 list(index 범위: 0 ~ 쿼리셋의 길이) => 실제 pk값과 매칭 필요
        #key : dataframe의 index, value : 쿼리셋의 pk 매칭해 딕셔너리화해준다
        pklist=list(result_list.values_list('pk', flat=True))
        index_dict={}
        for i in range(len(sortlist)):
            index_dict[i]=pklist[i]
        
        #pk_sortlist -> 쿼리셋의 pk로 tfidf 가중치 내림차순 정렬한 list
        pk_sortlist=[]
        for i in sortlist:
            pk_sortlist.append(index_dict[i])

        #검색결과 Queryset(result_list)를 pk_sortlist의 pk 순서대로 정렬
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_sortlist)])
        result_list =result_list.filter(pk__in=pk_sortlist).order_by(preserved)

        result_list_show=result_list
        context['sortlist']=sortlist
        context['pklist']=pklist
        context['resultlist']=result_list_show

    #한 페이지당 10개의 과목 데이터만 보여주기 위한 pagination
    paginator = Paginator(result_list, 10)
    page = request.GET.get('page',1)
        
    try:
        result_list = paginator.page(page)

    except PageNotAnInteger:
        result_list = paginator.page(1)

    except EmptyPage:
        result_list = paginator.page(paginator.num_pages)        

    #보여지는 페이지번호 리스트 5개로 제한 
    page_numbers_range = 5  
    max_index = len(paginator.page_range)
    current_page = int(page) if page else 1
    start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
    end_index = start_index + page_numbers_range
    if end_index >= max_index:
        end_index = max_index

    page_range = paginator.page_range[start_index:end_index]

    #template에 context data 전달
    context['form']=form
    context['sw']=searchWord
    context['lenword']=len(searchWord)
    context['object_list']=result_list
    context['y']=Year
    context['s']=Semester
    context['page_range'] = page_range

    return render(request, template_name, context)

##메인화면 검색창 ClassBasedView
class SearchView(FormView):   
    form_class=SubjectSearchForm
    template_name='subject/searchview.html'

    def form_valid(self, form):
        context={}
        context['form']=form

        return render(self.request, self.template_name, context)

##태그 포함 과목리스트 페이지 ClassBasedView
class TaggedObjectLV(ListView):
    template_name= 'subject/tagged_subject_list.html'
    model=Subject

    def get_context_data(self,*args, **kwargs):
        context=super().get_context_data(**kwargs)
        result_list=Subject.objects.filter(Q(tags__icontains=self.kwargs.get('tag')))
        tag=self.kwargs['tag']
        context['tagname']=tag
        
        #정렬 알고리즘 tf-idf / result_list 존재할때만 실행
        if result_list:
            #검색 결과 나온 Queryset(result_list)의 전체단어(words) 컬럼으로 tfidf 계산
            data=read_frame(result_list, fieldnames=['id', 'words'], index_col='id')
            A=data["words"].values.astype('U')
            tfidfv=TfidfVectorizer().fit(A)
            vocab_dict=tfidfv.vocabulary_
            B=tfidfv.transform(A).toarray()
            df=pd.DataFrame(B)

            #tfidfv 에서 검색단어에 해당하는 index 추출
            #검색단어가 전체단어리스트에 포함되어 있는 경우
            try: 
                id=vocab_dict[tag]

            #검색단어가 강의명, 교수명, 학과명이어서 전체단어리스트에 포함되어 있지 않는 경우
            except:
                id=1

            if id!=1:
                #검색 단어 index로 가중치 내림차순 정렬(가중치가 높을수록 검색단어의 과목 내 중요도가 높음)
                df=df.sort_values(by=[id], axis=0, ascending=[False])
                #list로 저장
                sortlist=list(df.index)

            # id=1일 때는 queryset dataframe index 단순 list화
            else:
                sortlist=list(df.index)

            #sortlist -> result_list를 dataframe 화하면서 새롭게 붙여진 index로 tfidf 가중치 내림차순 정렬한 list(index 범위: 0 ~ 쿼리셋의 길이) 
            #           => 실제 pk값과 매칭 필요
            #key : dataframe의 index, value : 쿼리셋의 pk 매칭해 딕셔너리화해준다
            pklist=list(result_list.values_list('pk', flat=True))
            index_dict={}
            for i in range(len(sortlist)):
                index_dict[i]=pklist[i]
            
            #pk_sortlist -> 쿼리셋의 pk로 tfidf 가중치 내림차순 정렬한 list
            pk_sortlist=[]
            for i in sortlist:
                pk_sortlist.append(index_dict[i])

            #검색결과 Queryset(result_list)를 pk_sortlist의 pk 순서대로 정렬
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_sortlist)])
            result_list =result_list.filter(pk__in=pk_sortlist).order_by(preserved)

            result_list_show=result_list
            context['list']=sortlist
            context['rl']=pklist
            context['resultlist']=result_list_show
        
        #한 페이지당 10개의 과목 데이터만 보여주기 위한 pagination
        paginator = Paginator(result_list, 10)
        page = self.request.GET.get('page',1)
        
        try:
            result_list = paginator.page(page)

        except PageNotAnInteger:
            result_list = paginator.page(1)

        except EmptyPage:
            result_list = paginator.page(paginator.num_pages)

        #보여지는 페이지번호 리스트 5개로 제한 
        page_numbers_range = 5  # Display only 5 page numbers
        max_index = len(paginator.page_range)
        current_page = int(page) if page else 1

        start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
        end_index = start_index + page_numbers_range
        if end_index >= max_index:
            end_index = max_index

        #template에 context data 전달
        context['page_range'] = paginator.page_range[start_index:end_index]
        context['object_list']=result_list
        
        return context
