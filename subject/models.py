from django.db import models
from django.utils.translation import gettext as _
from django.urls import reverse

class Subject(models.Model):
    YEAR_CHOICES=[(2020, '2020년'),(2021, '2021년')]
    SEMESTER_CHOICES=[('1R', '1학기'),('2R', '2학기')]

    id = models.IntegerField(primary_key=True)
    series_num=models.CharField(_("series_num"), blank=False,max_length=255)
    num=models.IntegerField(_("num"), blank=False) 
    name=models.CharField(_("name"), blank=False, max_length=255) 
    professor=models.CharField(_("professor"), blank=True, max_length=255) 
    department= models.CharField(_("department"),  blank=True, max_length=255) 
    category=models.CharField(_("category"),  blank=True, max_length=255) 
    grade= models.IntegerField(_("grade"), blank=True) 
    words_5= models.CharField(_("words"), blank=True, max_length=255)
    keywords_3=models.CharField(_("keywords"), blank=True, max_length=255)
    year=models.IntegerField(_("year"), blank=False, choices=YEAR_CHOICES)
    semester=models.CharField(_("semester"), blank=False, choices=SEMESTER_CHOICES,max_length=20) 
    tags=models.CharField(_("tags"), blank=True, max_length=255)
    words=models.TextField(_("words"), blank=True)

    recommend_subjects=models.ManyToManyField("self", symmetrical=False, through='RecommendSubject')

    class Meta:
        ordering=('num',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('subject:subject_detail', args=(self.series_num,))

#Recommend_subject N:N 관리 모델
class RecommendSubject(models.Model):
    subject=models.ForeignKey(Subject, on_delete=models.CASCADE, 
    related_name='recommend_subjects_rel')
    recommend_subject = models.ForeignKey(Subject, on_delete=models.CASCADE, 
    related_name='subjects')

class Kmooc(models.Model):
    id = models.IntegerField(primary_key=True)
    link= models.URLField(_("link")) 
    name = models.CharField(_("name"),  blank=False, max_length=255)
    image= models.CharField(_("image"),blank=False, max_length=255)
    midclassify=models.CharField(_("midclassify"), max_length=255)
    level= models.CharField(_("level"), max_length=255)

    subject_ids = models.ManyToManyField(Subject, blank=True, 
        through="SubjectKmooc",
        related_name="sub_moocs")

    def __str__(self):
        return self.name

#subject_Kmooc N:N 관리 모델
class SubjectKmooc(models.Model):
    subject= models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="subject_kmoocs"
    )

    kmooc= models.ForeignKey(
        Kmooc,
        on_delete=models.CASCADE,
        related_name="subject_kmoocs",
        db_index=True
    )
    
