from django.contrib import admin
from .models import Course, Enrollment, CourseModule, Lesson, Quiz, Question, Answer

class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'educator', 'level', 'is_published', 'created_at']
    list_filter = ['is_published', 'level', 'created_at']
    search_fields = ['title', 'description', 'educator__email']
    inlines = [CourseModuleInline]

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    inlines = [LessonInline]

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'quiz', 'question_type', 'points']
    inlines = [AnswerInline]

admin.site.register(Course, CourseAdmin)
admin.site.register(Enrollment)
admin.site.register(CourseModule, ModuleAdmin)
admin.site.register(Lesson)
admin.site.register(Quiz)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)