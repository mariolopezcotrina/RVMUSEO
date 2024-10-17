# quiz/management/commands/upload_quiz_data.py

import json
from django.core.management.base import BaseCommand
from api.models import Quiz, Pregunta, Opcion

class Command(BaseCommand):
    help = 'Carga datos de quiz desde un archivo JSON'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Ruta al archivo JSON con los datos del quiz')

    def handle(self, *args, **options):
        json_file = options['json_file']
        
        with open(json_file, 'r') as file:
            data = json.load(file)
        
        quiz = Quiz.objects.create(
            nombre_quiz=data['nombre_quiz'],
            descripcion=data['descripcion'],
            dificultad=data['dificultad'],
            tiempo_por_pregunta=data['tiempo_por_pregunta'],
            cantidad_preguntas=len(data['preguntas'])
        )
        
        for pregunta_data in data['preguntas']:
            pregunta = Pregunta.objects.create(
                quiz=quiz,
                texto_pregunta=pregunta_data['texto_pregunta']
            )
            
            for opcion_data in pregunta_data['opciones']:
                Opcion.objects.create(
                    pregunta=pregunta,
                    texto_opcion=opcion_data['texto_opcion'],
                    es_correcta=opcion_data['es_correcta']
                )
        
        self.stdout.write(self.style.SUCCESS(f'Quiz "{quiz.nombre_quiz}" cargado exitosamente'))