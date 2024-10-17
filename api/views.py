from django.shortcuts import render, redirect  # Asegúrate de tener también 'redirect'
from django.contrib.auth import authenticate, login, logout  # Importa 'login' aquí
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import Usuario, Quiz, Pregunta, Opcion, ResultadoQuiz, ExhibicionMuseo
from .serializers import UsuarioSerializer, RegistroSerializer, LoginSerializer, QuizSerializer, PreguntaSerializer, OpcionSerializer, QuizDetailSerializer, QuizDetailSerializer, ExhibicionMuseoSerializer, ResultadoQuizSerializer
import re


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    @action(detail=False, methods=['post'])
    def registro(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                # Validaciones adicionales
                nombre_usuario = serializer.validated_data['nombre_usuario']
                contraseña = serializer.validated_data['password']

                if not re.match(r'^[a-zA-Z0-9_]{4,20}$', nombre_usuario):
                    return Response(
                        {"error": "El nombre de usuario debe tener entre 4 y 20 caracteres y solo puede contener letras, números y guiones bajos."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if len(contraseña) < 8:
                    return Response(
                        {"error": "La contraseña debe tener al menos 8 caracteres."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Hashear la contraseña antes de guardar
                serializer.validated_data['password'] = make_password(contraseña)
                usuario = serializer.save()

                # Generar el token para el usuario registrado
                token, created = Token.objects.get_or_create(user=usuario)

                # Retornar los datos del usuario y el token
                return Response({
                    "user": self.get_serializer(usuario).data,
                    "token": token.key
                }, status=status.HTTP_201_CREATED)

            except IntegrityError:
                return Response(
                    {"error": "El nombre de usuario ya está en uso."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        # Redirigir las solicitudes POST estándar al método de registro
        return self.registro(request)

    @action(detail=False, methods=['post'])
    @method_decorator(csrf_exempt)
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            nombre_usuario = serializer.validated_data['nombre_usuario']
            password = serializer.validated_data['password']
            user = authenticate(nombre_usuario=nombre_usuario, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                response = Response({
                    "user": UsuarioSerializer(user).data,
                    "token": token.key
                })
                if request.data.get('remember_me', False):
                    response.set_cookie('auth_token', token.key, max_age=30*24*60*60, httponly=True)
                return response
            return Response({"error": "Credenciales inválidas"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        if request.user.is_authenticated:
            request.user.auth_token.delete()
        response = Response({"message": "Sesión cerrada exitosamente"})
        response.delete_cookie('auth_token')
        return response

    @action(detail=False, methods=['get', 'put', 'patch'])
    def perfil(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    @action(detail=True, methods=['get'])
    def detalle(self, request, pk=None):
        quiz = self.get_object()
        serializer = QuizDetailSerializer(quiz)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def submit_quiz(self, request, pk=None):
        quiz = self.get_object()
        usuario = request.user
        puntuacion = request.data.get('puntuacion', 0)
        mensaje = request.data.get('mensaje', '')
        
        # Asegurarse de que la puntuación no exceda la puntuación máxima del quiz
        puntuacion = min(puntuacion, quiz.puntuacion_maxima)
        
        resultado = ResultadoQuiz.objects.create(
            usuario=usuario,
            quiz=quiz,
            puntuacion=puntuacion,
            mensaje=mensaje
        )
        
        serializer = ResultadoQuizSerializer(resultado)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PreguntaViewSet(viewsets.ModelViewSet):
    queryset = Pregunta.objects.all()
    serializer_class = PreguntaSerializer

class OpcionViewSet(viewsets.ModelViewSet):
    queryset = Opcion.objects.all()
    serializer_class = OpcionSerializer

class ResultadoQuizViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResultadoQuiz.objects.all()
    serializer_class = ResultadoQuizSerializer

    def get_queryset(self):
        return ResultadoQuiz.objects.filter(usuario=self.request.user)
    
    @action(detail=False, methods=['get'])
    def ultimo(self, request):
        ultimo_resultado = self.get_queryset().order_by('-completado_en').first()
        if ultimo_resultado:
            serializer = self.get_serializer(ultimo_resultado)
            return Response(serializer.data)
        return Response({"detail": "No hay resultados disponibles"}, status=status.HTTP_404_NOT_FOUND)

class ExhibicionMuseoViewSet(viewsets.ModelViewSet):
    queryset = ExhibicionMuseo.objects.all()
    serializer_class = ExhibicionMuseoSerializer

# ... (otras vistas como login_view, logout_view, dashboard, etc.)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Aquí ya puedes usar 'login'
            return redirect('dashboard')
        else:
            return render(request, 'dashboard/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'dashboard/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    context = {
        'usuarios_count': Usuario.objects.count(),
        'quizzes_count': Quiz.objects.count(),
        'resultados_count': ResultadoQuiz.objects.count(),
        'exhibiciones_count': ExhibicionMuseo.objects.count(),
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'dashboard/usuarios.html', {'usuarios': usuarios})

@login_required
def quizzes(request):
    quizzes = Quiz.objects.all()
    return render(request, 'dashboard/quizzes.html', {'quizzes': quizzes})

@login_required
def resultados(request):
    resultados = ResultadoQuiz.objects.all()
    return render(request, 'dashboard/resultados.html', {'resultados': resultados})