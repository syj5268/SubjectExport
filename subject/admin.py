from django.contrib import admin
from subject.models import *

# Register your models here.
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display=('id','series_num',"num", "name", "professor",
        "department", "category", "grade", "words_5","keywords_3", 'year','semester','tags','recommend_sub_list')
    list_editable =("words_5","keywords_3",'tags')
    search_fields=('id','series_num','name',"professor","department","words_5","keywords_3",'year','semester','tags')

    def recommend_sub_list(self, obj):
        return ','.join(o.name for o in obj.recommend_subjects.all())
    
# @admin.register(Kmooc)
# class KmoocAdmin(admin.ModelAdmin):
#     list_display=('id','midclassify', "name", "level",
#         "image", "link",'sub_list')

#     search_fields=('id', "name",'sub_list')

#     def sub_list(self, obj):
#         return ','.join(o.name for o in obj.subject_ids.all())
    
# @admin.register(SubjectKmooc)
# class SubjectKmoocAdmin(admin.ModelAdmin):
#     list_display=('subject','kmooc')
#     search_fields=('subject','kmooc')
#     list_editable =('kmooc',)

# @admin.register(RecommendSubject)
# class RecommendSubjectAdmin(admin.ModelAdmin):
#     list_display=('subject','recommend_subject')
#     search_fields=('subject','recommend_subject')
#     list_editable =('recommend_subject',)

    
