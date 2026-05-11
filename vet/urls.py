from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/',   views.login_view,  name='login'),
    path('logout/',  views.logout_view, name='logout'),
    # Home
    path('', views.index, name='index'),
    # Dueños
    path('duenos/',                       views.duenos,         name='duenos'),
    path('duenos/crear/',                 views.crear_dueno,    name='crear_dueno'),
    path('duenos/editar/<int:id>/',       views.editar_dueno,   name='editar_dueno'),
    path('duenos/eliminar/<int:id>/',     views.eliminar_dueno, name='eliminar_dueno'),
    # Mascotas
    path('mascotas/',                     views.mascotas,        name='mascotas'),
    path('mascotas/crear/',               views.crear_mascota,   name='crear_mascota'),
    path('mascotas/editar/<int:id>/',     views.editar_mascota,  name='editar_mascota'),
    path('mascotas/eliminar/<int:id>/',   views.eliminar_mascota,name='eliminar_mascota'),
    # Consultas
    path('consultas/',                    views.consultas,        name='consultas'),
    path('consultas/crear/',              views.crear_consulta,   name='crear_consulta'),
    path('consultas/editar/<int:id>/',    views.editar_consulta,  name='editar_consulta'),
    path('consultas/eliminar/<int:id>/',  views.eliminar_consulta,name='eliminar_consulta'),
    # Informe
    path('informe/', views.informe, name='informe'),
]
