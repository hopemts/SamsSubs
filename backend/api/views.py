from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
import snowflake.connector
import os
from dotenv import load_dotenv
import logging
import traceback

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create your views here.

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello, World!"})

@api_view(['POST'])
def login(request):
    phone_number = request.data.get('phone_number')
    if not phone_number:
        return Response({'message': 'Phone number is required'}, status=400)
    
    try:
        # Connect to Snowflake
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        )
        
        # Check if the phone number exists in the CUSTOMER_DIM table
        cursor = conn.cursor()
        cursor.execute("SELECT CUSTOMERKEY, CUSTOMERFNAME, CUSTOMERLNAME FROM CUSTOMER_DIM WHERE CUSTOMERPHONE = %s", (phone_number,))
        result = cursor.fetchone()
        
        if result:
            # If the phone number is found, return success with user data
            user_data = {
                'customer_key': result[0],
                'first_name': result[1],
                'last_name': result[2]
            }
            return Response({
                'message': 'Login successful',
                'user': user_data
            }, status=200)
        else:
            # If the phone number is not found, return a message
            return Response({'message': 'Phone number not found in records'}, status=404)
    
    except Exception as e:
        return Response({'message': f'Error checking phone number: {str(e)}'}, status=500)
    finally:
        if 'conn' in locals():
            conn.close()

@api_view(['GET'])
def get_sandwich_details(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        
        # Get Snowflake connection parameters
        snowflake_params = {
            'user': os.getenv('SNOWFLAKE_USER'),
            'password': os.getenv('SNOWFLAKE_PASSWORD'),
            'account': os.getenv('SNOWFLAKE_ACCOUNT'),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
            'database': os.getenv('SNOWFLAKE_DATABASE'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA')
        }
        
        # Connect to Snowflake
        conn = snowflake.connector.connect(**snowflake_params)
        
        try:
            cur = conn.cursor()
            
            # Check if the sandwich_details table exists
            logger.info("Checking if sandwich_details table exists...")
            cur.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = %s 
                AND table_name = 'SANDWICH_DETAILS'
            """, (snowflake_params['schema'],))
            
            table_exists = cur.fetchone()[0] > 0
            if not table_exists:
                logger.error("sandwich_details table does not exist in the specified schema")
                return Response({
                    'message': 'Sandwich details are not available at this time',
                    'user': UserSerializer(user).data,
                    'sandwich_details': []
                })
            
            # Get table columns
            logger.info("Getting sandwich_details table columns...")
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = %s 
                AND table_name = 'SANDWICH_DETAILS'
            """, (snowflake_params['schema'],))
            
            columns = cur.fetchall()
            logger.info(f"Table columns: {columns}")
            
            # Execute the query to get sandwich details
            logger.info(f"Executing query to get sandwich details for user_id: {user_id}")
            cur.execute("""
                SELECT * FROM sandwich_details 
                WHERE customer_id = %s
            """, (user_id,))
            
            results = cur.fetchall()
            
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
            
        except snowflake.connector.errors.ProgrammingError as e:
            logger.error(f"Snowflake query error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response({
                'message': 'Error retrieving sandwich details',
                'user': UserSerializer(user).data,
                'sandwich_details': []
            })
        finally:
            cur.close()
            conn.close()
            logger.info("Snowflake connection closed")
            
    except User.DoesNotExist:
        return Response({
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response({
            'message': 'An unexpected error occurred'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def test_snowflake_connection(request):
    try:
        # Get Snowflake connection parameters
        snowflake_params = {
            'user': os.getenv('SNOWFLAKE_USER'),
            'password': os.getenv('SNOWFLAKE_PASSWORD'),
            'account': os.getenv('SNOWFLAKE_ACCOUNT'),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
            'database': os.getenv('SNOWFLAKE_DATABASE'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA')
        }
        
        # Log connection parameters (without sensitive data)
        logger.info(f"Testing Snowflake connection with account: {snowflake_params['account']}")
        
        # Connect to Snowflake
        conn = snowflake.connector.connect(**snowflake_params)
        
        try:
            # Execute a simple test query
            cur = conn.cursor()
            cur.execute("SELECT current_version()")
            version = cur.fetchone()[0]
            cur.close()
            
            return Response({
                'message': 'Successfully connected to Snowflake',
                'version': version
            })
            
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Snowflake connection test failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response({
            'message': f'Connection test failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def check_customer_table(request):
    try:
        # Get Snowflake connection parameters
        snowflake_params = {
            'user': os.getenv('SNOWFLAKE_USER'),
            'password': os.getenv('SNOWFLAKE_PASSWORD'),
            'account': os.getenv('SNOWFLAKE_ACCOUNT'),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
            'database': os.getenv('SNOWFLAKE_DATABASE'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA')
        }
        
        # Log connection parameters (excluding password)
        safe_params = snowflake_params.copy()
        safe_params['password'] = '********'
        logger.info(f"Attempting to connect to Snowflake with parameters: {safe_params}")
        
        # Connect to Snowflake
        conn = snowflake.connector.connect(**snowflake_params)
        
        try:
            cur = conn.cursor()
            
            # Get current schema
            cur.execute("SELECT CURRENT_SCHEMA()")
            current_schema = cur.fetchone()[0]
            logger.info(f"Current schema: {current_schema}")
            
            # List all tables in the schema
            logger.info(f"Listing all tables in schema: {current_schema}")
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s
            """, (current_schema,))
            
            tables = cur.fetchall()
            logger.info(f"Tables in schema: {tables}")
            
            # Check if the customer_dim table exists (case-insensitive)
            logger.info("Checking if customer_dim table exists...")
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s 
                AND upper(table_name) = 'CUSTOMER_DIM'
            """, (current_schema,))
            
            table_result = cur.fetchone()
            table_exists = table_result is not None
            
            if not table_exists:
                return Response({
                    'message': 'customer_dim table does not exist',
                    'exists': False,
                    'available_tables': [table[0] for table in tables]
                })
            
            actual_table_name = table_result[0]
            logger.info(f"Found table with name: {actual_table_name}")
            
            # Get table columns
            logger.info("Getting customer_dim table columns...")
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = %s 
                AND table_name = %s
            """, (current_schema, actual_table_name))
            
            columns = cur.fetchall()
            logger.info(f"Table columns: {columns}")
            
            # Check if required columns exist
            required_columns = {'CUSTOMERPHONE', 'CUSTOMER_ID', 'FIRST_NAME', 'LAST_NAME'}
            existing_columns = {col[0].upper() for col in columns}
            missing_columns = required_columns - existing_columns
            
            # Get a sample row
            cur.execute(f"SELECT * FROM {current_schema}.{actual_table_name} LIMIT 1")
            sample_row = cur.fetchone()
            
            return Response({
                'message': 'Table check completed',
                'exists': True,
                'table_name': actual_table_name,
                'columns': columns,
                'missing_columns': list(missing_columns) if missing_columns else [],
                'sample_row': sample_row if sample_row else None
            })
            
        finally:
            cur.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"Error checking customer_dim table: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response({
            'message': f'Error checking table: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def inspect_tables(request):
    try:
        # Get Snowflake connection parameters
        snowflake_params = {
            'user': os.getenv('SNOWFLAKE_USER'),
            'password': os.getenv('SNOWFLAKE_PASSWORD'),
            'account': os.getenv('SNOWFLAKE_ACCOUNT'),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
            'database': os.getenv('SNOWFLAKE_DATABASE'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA')
        }
        
        # Log connection parameters (excluding password)
        safe_params = snowflake_params.copy()
        safe_params['password'] = '********'
        logger.info(f"Attempting to connect to Snowflake with parameters: {safe_params}")
        
        # Connect to Snowflake
        conn = snowflake.connector.connect(**snowflake_params)
        
        try:
            cur = conn.cursor()
            
            # First verify we can connect and get current schema
            cur.execute("SELECT CURRENT_SCHEMA()")
            current_schema = cur.fetchone()[0]
            logger.info(f"Current schema: {current_schema}")
            
            # Use the current schema instead of the environment variable
            target_schema = current_schema
            
            # List all schemas in the database
            cur.execute("""
                SELECT DISTINCT table_schema 
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('INFORMATION_SCHEMA')
                ORDER BY table_schema
            """)
            schemas = cur.fetchall()
            logger.info(f"Available schemas: {schemas}")
            
            # List all tables without schema filter first
            cur.execute("""
                SELECT table_schema, table_name, table_type
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('INFORMATION_SCHEMA')
                ORDER BY table_schema, table_name
            """)
            all_tables = cur.fetchall()
            logger.info(f"All tables in database: {all_tables}")
            
            # Now try to get tables in our target schema
            cur.execute("""
                SELECT table_name, table_type
                FROM information_schema.tables 
                WHERE table_schema = %s
                ORDER BY table_name
            """, (target_schema,))
            
            schema_tables = cur.fetchall()
            logger.info(f"Tables in schema {target_schema}: {schema_tables}")
            
            # For each table in our schema, get its structure and a sample row
            table_info = {}
            for table in schema_tables:
                table_name = table[0]
                table_type = table[1]
                logger.info(f"Processing table: {table_name} (type: {table_type})")
                
                # Get columns
                cur.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = %s 
                    AND table_name = %s
                    ORDER BY ordinal_position
                """, (target_schema, table_name))
                
                columns = cur.fetchall()
                logger.info(f"Found {len(columns)} columns in {table_name}")
                
                # Get sample row
                try:
                    cur.execute(f"SELECT * FROM {target_schema}.{table_name} LIMIT 1")
                    sample_row = cur.fetchone()
                    logger.info(f"Got sample row from {table_name}")
                except Exception as e:
                    logger.error(f"Error getting sample row from {table_name}: {str(e)}")
                    sample_row = None
                
                table_info[table_name] = {
                    'type': table_type,
                    'columns': [{'name': col[0], 'type': col[1]} for col in columns],
                    'sample_row': sample_row
                }
            
            return Response({
                'message': 'Table inspection completed',
                'current_schema': current_schema,
                'target_schema': target_schema,
                'available_schemas': [schema[0] for schema in schemas],
                'all_tables': [{'schema': t[0], 'name': t[1], 'type': t[2]} for t in all_tables],
                'schema_tables': table_info
            })
            
        finally:
            cur.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"Error inspecting tables: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response({
            'message': f'Error inspecting tables: {str(e)}',
            'error_details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_customer_favorite_sandwich(request, customer_key):
    try:
        # Connect to Snowflake
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        )
        
        cursor = conn.cursor()
        
        # Query to get the most ordered sandwich for the customer
        query = """
        WITH OrderCounts AS (
            SELECT 
                f.CUSTOMERKEY,
                f.PRODUCTKEY,
                p.PRODUCTNAME,
                SUM(f.QUANTITY) as total_ordered,
                ROW_NUMBER() OVER (PARTITION BY f.CUSTOMERKEY ORDER BY SUM(f.QUANTITY) DESC) as rank
            FROM FACT_ORDERPROCESSING f
            JOIN PRODUCT_DIM p ON f.PRODUCTKEY = p.PRODUCTKEY
            WHERE f.CUSTOMERKEY = %s
            GROUP BY f.CUSTOMERKEY, f.PRODUCTKEY, p.PRODUCTNAME
        )
        SELECT 
            PRODUCTNAME,
            total_ordered
        FROM OrderCounts
        WHERE rank = 1
        """
        
        cursor.execute(query, (customer_key,))
        result = cursor.fetchone()
        
        if result:
            favorite_sandwich = {
                'product_name': result[0],
                'total_ordered': result[1]
            }
            return Response(favorite_sandwich, status=200)
        else:
            return Response({'message': 'No orders found for this customer'}, status=404)
            
    except Exception as e:
        return Response({'message': f'Error retrieving favorite sandwich: {str(e)}'}, status=500)
    finally:
        if 'conn' in locals():
            conn.close()

@api_view(['GET'])
def get_customer_sandwich_report(request, customer_key):
    try:
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        )
        
        cursor = conn.cursor()
        
        # 1. Favorite Sandwich (Most Ordered)
        favorite_query = """
        WITH OrderCounts AS (
            SELECT 
                f.PRODUCTKEY,
                p.PRODUCTNAME,
                p.PRODUCTCALORIES,
                SUM(f.QUANTITY) as total_ordered,
                ROW_NUMBER() OVER (PARTITION BY f.CUSTOMERKEY ORDER BY SUM(f.QUANTITY) DESC) as rank
            FROM FACT_ORDERPROCESSING f
            JOIN PRODUCT_DIM p ON f.PRODUCTKEY = p.PRODUCTKEY
            WHERE f.CUSTOMERKEY = %s
            GROUP BY f.CUSTOMERKEY, f.PRODUCTKEY, p.PRODUCTNAME, p.PRODUCTCALORIES
        )
        SELECT 
            PRODUCTNAME,
            PRODUCTCALORIES,
            total_ordered
        FROM OrderCounts
        WHERE rank = 1
        """
        
        # 2. Total Sandwiches Ordered
        total_query = """
        SELECT 
            COUNT(DISTINCT f.DATEKEY) as unique_days,
            SUM(f.QUANTITY) as total_sandwiches,
            SUM(f.QUANTITY * f.PRICE_EACH) as total_spent
        FROM FACT_ORDERPROCESSING f
        WHERE f.CUSTOMERKEY = %s
        """
        
        # 3. Favorite Order Method
        method_query = """
        WITH MethodCounts AS (
            SELECT 
                m.ORDERMETHOD,
                COUNT(*) as method_count,
                ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) as rank
            FROM FACT_ORDERPROCESSING f
            JOIN ORDERMETHOD_DIM m ON f.METHODKEY = m.METHODKEY
            WHERE f.CUSTOMERKEY = %s
            GROUP BY m.ORDERMETHOD
        )
        SELECT 
            ORDERMETHOD,
            method_count
        FROM MethodCounts
        WHERE rank = 1
        """
        
        # 4. Most Common Store
        store_query = """
        WITH StoreCounts AS (
            SELECT 
                s.CITY,
                s.ADDRESS,
                COUNT(*) as visit_count,
                ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) as rank
            FROM FACT_ORDERPROCESSING f
            JOIN STORE_DIM s ON f.STOREKEY = s.STOREKEY
            WHERE f.CUSTOMERKEY = %s
            GROUP BY s.CITY, s.ADDRESS
        )
        SELECT 
            CITY,
            ADDRESS,
            visit_count
        FROM StoreCounts
        WHERE rank = 1
        """
        
        # 5. Order History Timeline
        timeline_query = """
        SELECT 
            d.MONTH_NAME,
            d.YEAR_NUMBER,
            d.MONTH_OF_YEAR,
            SUM(f.QUANTITY) as sandwiches_that_month
        FROM FACT_ORDERPROCESSING f
        JOIN DATE_DIM d ON f.DATEKEY = d.DATEKEY
        WHERE f.CUSTOMERKEY = %s
        GROUP BY d.MONTH_NAME, d.YEAR_NUMBER, d.MONTH_OF_YEAR
        ORDER BY d.YEAR_NUMBER DESC, d.MONTH_OF_YEAR DESC
        LIMIT 6
        """
        
        # Execute all queries
        cursor.execute(favorite_query, (customer_key,))
        favorite_result = cursor.fetchone()
        
        cursor.execute(total_query, (customer_key,))
        total_result = cursor.fetchone()
        
        cursor.execute(method_query, (customer_key,))
        method_result = cursor.fetchone()
        
        cursor.execute(store_query, (customer_key,))
        store_result = cursor.fetchone()
        
        cursor.execute(timeline_query, (customer_key,))
        timeline_results = cursor.fetchall()
        
        if not favorite_result:
            return Response({'message': 'No orders found for this customer'}, status=404)
            
        # Compile the report
        report = {
            'favorite_sandwich': {
                'name': favorite_result[0],
                'calories': favorite_result[1],
                'times_ordered': favorite_result[2]
            },
            'order_stats': {
                'unique_days_ordered': total_result[0],
                'total_sandwiches': total_result[1],
                'total_spent': float(total_result[2]) if total_result[2] else 0
            },
            'preferred_ordering': {
                'method': method_result[0] if method_result else None,
                'times_used': method_result[1] if method_result else 0
            },
            'favorite_location': {
                'city': store_result[0] if store_result else None,
                'address': store_result[1] if store_result else None,
                'visits': store_result[2] if store_result else 0
            },
            'order_timeline': [
                {
                    'month': result[0],
                    'year': result[1],
                    'sandwiches': result[3]
                }
                for result in timeline_results
            ]
        }
        
        return Response(report, status=200)
            
    except Exception as e:
        return Response({'message': f'Error generating sandwich report: {str(e)}'}, status=500)
    finally:
        if 'conn' in locals():
            conn.close()
