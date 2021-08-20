과목 수강 ‘전’ 과정을 책임지는 <과목 박사> 서비스

About The Project
--------------------

학생들은 학기 중 들을 수업을 고르기 위해 많은 고민을 하고, 전공 외에도 다양한 수업에 대한 갈망이 있으며, 수강한 수업을 바탕으로 진로를 탐색한다. <과목 박사> 서비스를 통해 학생들이 본인들의 관심사를 바탕으로 관련 과목을 찾을 수 있도록 돕고, 수강 과목과 관련된 추가적인 강의 컨텐츠를 추천해줌으로써 학생들의 학업을 돕고자 한다. 궁극적으로 학생들의 학업을 도울 수 있는 스마트 캠퍼스를 구현하고자 한다.

Overview
--------------------

키워드 검색 기능, 유사 강의 추천 기능, K-MOOC 강의 추천 기능, 관련 도서 추천 기능을 통해 과목 탐색 과정을 개선하고, 학습도구를 지원하고자 한다. Django를 통해 Web 사이트에 다음의 기능들을 모두 구현하였다.

Project Files Description
--------------------

<Django - SubjectExpert >
웹 서비스 구현을 위한 코드 zip

*requirements.txt
필요한 python module 목록

*views.py 
(SearchView CBV)
-> forms.py 에서 Request 받아서 검색 ORM 진행

(Search FBV)
-> 키워드 검색 - views.py (Search FBV)
	-> 키워드 검색 결과 존재 할 때 - tfidf 가중치 순 정렬
-> 학기별 구분 검색, 교수명, 과목명, 학과명, 학수번호 검색 가능

(SubjectDV CBV)
-> 과목정보
	-> 워드클라우드 생성 (template - subject_detail.html 에서  
-> 유사강의 추천, K-MOOC 추천, 교재 추천 (Naver API 연결)

(TaggedObjectLV CBV)
-> 상세 페이지에서 워드 클라우드에 있는 키워드 클릭 시 해당 키워드 포함 과목 보여주는 ORM 진행

(templates - components : 네비게이션 바, 검색 입력란, 버튼, 로고 등 페이지 구성 요소)

(templates - subject : 페이지 구성)
*searchview.html 메인화면 검색창 페이지
*Resultlist.html 검색 결과 페이지
*subject_detail.html 과목 상세 페이지
*tagged_object_list.html 키워드 태그 포함 과목 리스트 페이지
