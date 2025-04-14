from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
import snowflake.connector
import os

# Create your views here.

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello, World!"})

@api_view(['POST'])
def login(request):
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    
    try:
        user = User.objects.get(first_name=first_name, last_name=last_name)
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data
        })
    except User.DoesNotExist:
        return Response({
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_sandwich_details(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        
        # Snowflake connection details - these should be in environment variables
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        )
        
        # Example query - modify according to your Snowflake schema
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM sandwich_details 
            WHERE customer_id = %s
        """, (user_id,))
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        # Transform results into a list of dictionaries
        sandwich_details = []
        for row in results:
            sandwich_details.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                # Add more fields as needed
            })
        
        return Response({
            'user': UserSerializer(user).data,
            'sandwich_details': sandwich_details
        })
        
    except User.DoesNotExist:
        return Response({
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
