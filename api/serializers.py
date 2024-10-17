from rest_framework import serializers
from .models import Usuario, Quiz, Pregunta, Opcion, ResultadoQuiz, ExhibicionMuseo

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['nombre_usuario', 'first_name', 'last_name', 'password', 'indice_avatar']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    nombre_usuario = serializers.CharField()
    password = serializers.CharField()

class OpcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opcion
        fields = ['id', 'texto_opcion', 'es_correcta']

class PreguntaSerializer(serializers.ModelSerializer):
    opciones = OpcionSerializer(many=True, read_only=True)

    class Meta:
        model = Pregunta
        fields = ['id', 'texto_pregunta', 'opciones']

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'nombre_quiz', 'descripcion', 'dificultad', 'tiempo_por_pregunta', 'cantidad_preguntas', 'puntuacion_maxima']

class QuizDetailSerializer(serializers.ModelSerializer):
    preguntas = PreguntaSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'nombre_quiz', 'descripcion', 'dificultad', 'tiempo_por_pregunta', 'cantidad_preguntas', 'puntuacion_maxima', 'preguntas']

class ResultadoQuizSerializer(serializers.ModelSerializer):
    nombre_quiz = serializers.CharField(source='quiz.nombre_quiz', read_only=True)
    nombre_usuario = serializers.CharField(source='usuario.nombre_usuario', read_only=True)
    puntuacion_maxima = serializers.IntegerField(source='quiz.puntuacion_maxima', read_only=True)

    class Meta:
        model = ResultadoQuiz
        fields = ['id', 'nombre_quiz', 'nombre_usuario', 'puntuacion', 'puntuacion_maxima', 'completado_en']
        read_only_fields = ['completado_en']

class ExhibicionMuseoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExhibicionMuseo
        fields = '__all__'