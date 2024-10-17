# api/models.py

# from django.db import models

# class Usuario(models.Model):
#     nombre_usuario = models.CharField(max_length=255, unique=True)
#     first_name = models.CharField(max_length=255)
#     last_name = models.CharField(max_length=255)
#     password = models.CharField(max_length=255)
#     indice_avatar = models.IntegerField()
#     creado_en = models.DateTimeField(auto_now_add=True)

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, nombre_usuario, password=None, **extra_fields):
        if not nombre_usuario:
            raise ValueError('El nombre de usuario es obligatorio')
        user = self.model(nombre_usuario=nombre_usuario, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nombre_usuario, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(nombre_usuario, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre_usuario = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    indice_avatar = models.IntegerField()
    creado_en = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'indice_avatar']

    def __str__(self):
        return self.nombre_usuario

class Quiz(models.Model):
    DIFICULTAD_CHOICES = [
        ('F', 'Fácil'),
        ('M', 'Medio'),
        ('D', 'Difícil'),
    ]
    nombre_quiz = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    dificultad = models.CharField(max_length=1, choices=DIFICULTAD_CHOICES, default='M')
    tiempo_por_pregunta = models.FloatField(default=15.0)
    cantidad_preguntas = models.IntegerField(default=15)
    puntuacion_maxima = models.IntegerField(default=20)  # Nueva campo para la puntuación máxima

    def __str__(self):
        return self.nombre_quiz

class Pregunta(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='preguntas', on_delete=models.CASCADE)
    texto_pregunta = models.TextField()

    def __str__(self):
        return self.texto_pregunta[:50]

class Opcion(models.Model):
    pregunta = models.ForeignKey(Pregunta, related_name='opciones', on_delete=models.CASCADE)
    texto_opcion = models.TextField()
    es_correcta = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.texto_opcion[:30]} - {'Correcta' if self.es_correcta else 'Incorrecta'}"
    
    def clean(self):
        if self.es_correcta:
            correctas = Opcion.objects.filter(pregunta=self.pregunta, es_correcta=True).exclude(pk=self.pk)
            if correctas.exists():
                raise ValidationError("Solo puede haber una opción correcta por pregunta.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class ResultadoQuiz(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    # puntuacion = models.IntegerField()
    puntuacion = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(20)])
    mensaje = models.TextField()  # Nuevo campo para almacenar el mensaje completo
    completado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-puntuacion', '-completado_en']

    # def __str__(self):
    #     return f"{self.usuario.nombre_usuario} - {self.quiz.nombre_quiz}: {self.puntuacion}"
    def __str__(self):
        return f"{self.usuario.nombre_usuario} - {self.quiz.nombre_quiz}: {self.puntuacion}/{self.quiz.puntuacion_maxima}"

class ExhibicionMuseo(models.Model):
    nombre_exhibicion = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    nombre_escena = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre_exhibicion