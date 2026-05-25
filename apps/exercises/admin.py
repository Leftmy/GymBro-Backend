from django.contrib import admin

from .models import Exercise, MuscleGroup, ExerciseMuscle


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
	list_display = ("name", "difficulty", "equipment")
	list_filter = ("difficulty", "equipment")
	search_fields = ("name", "description")
	raw_id_fields = ("muscles",)


@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
	list_display = ("name", "slug", "svg_id")
	search_fields = ("name", "slug")


@admin.register(ExerciseMuscle)
class ExerciseMuscleAdmin(admin.ModelAdmin):
	list_display = ("id", "exercise", "muscle")
	raw_id_fields = ("exercise", "muscle")
