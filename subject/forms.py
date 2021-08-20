from django import forms

YEAR_CHOICES=[
    ('-', '전체연도'),
    (2020, '2020년'),
    (2021, '2021년')
]

SEMESTER_CHOICES=[
    ('-', '전체학기'),
    ('1R', '1학기'),
    ('2R', '2학기')
]

class SubjectSearchForm(forms.Form):
    search_word=forms.CharField(widget=forms.TextInput(attrs={'class': 'homeform', 'name':'search_word', 'placeholder':"키워드로 강의를 찾아보세요:)"}))
    year=forms.ChoiceField(required=False, label='년도', widget=forms.Select(attrs={"class":'choices', 'name':'year'}), choices=YEAR_CHOICES)
    semester=forms.ChoiceField(required=False, label='학기',widget=forms.Select(attrs={"class":'choices', 'name':'semester'}), choices=SEMESTER_CHOICES)