from .forms import RegistroUsuarioForm, ComentarioForm
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import *
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Usuario
from ..posts.models import Comentario, Post


class RegistrarUsuario(CreateView):
     template_name = 'registration/registrar.html'
     form_class = RegistroUsuarioForm

     def form_valid(self, form):
          response = super().form_valid(form)
          messages.success(self.request, 'Registro exitoso. Por favor, inicia sesión.')
          group = Group.objects.get(name='Registrado')
          self.object.groups.add(group)
          return redirect('apps.usuario:registrar')

class LoginUsuario(LoginView):
     template_name = 'registration/login.html'

     def get_success_url(self):
          messages.success(self.request, 'Login exitoso')

          return reverse('apps.usuario:login')

class LogoutUsuario(LogoutView):
     template_name = 'registration/logout.html'

     def get_success_url(self):
          messages.success(self.request, 'Logout exitoso')

          return reverse('apps.usuario:logout')   

class UsuarioListView(LoginRequiredMixin, ListView):
     model = Usuario
     template_name = 'usuario/usuario_list.html'
     context_object_name = 'usuarios'

     def get_queryset(self):
      queryset = super().get_queryset()
      queryset = queryset.exclude(is_superuser=True)
      return queryset

class UsuarioDeleteView(LoginRequiredMixin, DeleteView):
     model = Usuario
     template_name = 'usuario/eliminar_usuario.html'
     success_url = reverse_lazy('apps.usuario:usuario_list')              

     def get_context_data(self, **kwargs):
          context = super().get_context_data(**kwargs) 
          colaborador_group = Group.objects.get(name='Colaborador')
          es_colaborador = colaborador_group in self.object.groups.all()
          context['es_colaborador'] = es_colaborador
          return context

     def post(self, request, *args, **kwargs):
           eliminar_comentarios = request.POST.get('eliminar_comentarios', False)
           eliminar_posts = request.POST.get('eliminar_posts', False)
           self.object = self.get_object()
           if eliminar_comentarios:
               Comentario.objects.filter(usuario=self.object).delete()

           if eliminar_posts:
               Post.objects.filter(autor=self.object).delete()
           messages.success(request, f'Usuario {self.object.username} eliminado correctamente')
           return self.delete(request, *args, **kwargs)              

class ComentarioUpdateView(LoginRequiredMixin, UpdateView):
           model = ComentarioForm
           form_class = ComentarioForm
           template_name = 'comentario/comentario_form.html'

           def get_success_url(self):
               next_url = self.request.GET.get('next')
               if next_url:
                   return next_url
               else:
                   return reverse('apps.posts:post_individual', args=[self.object.post.id])

class ComentarioDeleteView(LoginRequiredMixin, DeleteView):
           model = Comentario
           template_name = 'comentario/comentario_confirm_delete.html'

           def get_success_url(self):
                 
                return reverse('apps.posts:post_individual', args=(self.object.posts.id))            