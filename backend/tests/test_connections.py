# backend/test_connections.py
import os
import sys
from dotenv import load_dotenv
import stripe
import httpx
import asyncio

# Load environment variables
load_dotenv()

def test_pinecone():
    print("Testing Pinecone connection...")
    try:
        from pinecone import Pinecone # Remove the .grpc part
        
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index_name = os.getenv("PINECONE_INDEX")
        
        if index_name in pc.list_indexes().names():
            print(f"✓ Pinecone connection successful! Index '{index_name}' found.")
        else:
            print(f"✗ Pinecone index '{index_name}' not found. Available indexes: {pc.list_indexes().names()}")
    except Exception as e:
        print(f"✗ Pinecone connection failed: {str(e)}")

def test_gemini():
    print("Testing Google Gemini connection...")
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # List available models to see what's available
        models = genai.list_models()
        model_names = [model.name for model in models]
        print(f"Available models: {model_names}")
        
        # Use a model that's actually available
        model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
        response = model.generate_content("Hello, what is 1+1?")
        print(f"✓ Gemini connection successful! Response: {response.text}")
    except Exception as e:
        print(f"✗ Gemini connection failed: {str(e)}")

def test_stripe():
    print("Testing Stripe connection...")
    try:
        stripe_key = os.getenv("STRIPE_API_KEY")
        if not stripe_key or stripe_key.startswith("ysk_test"):
            print("✗ Stripe connection failed: You're using a placeholder API key. Please use your actual Stripe API key.")
            return
            
        stripe.api_key = stripe_key
        products = stripe.Product.list(limit=1)
        print(f"✓ Stripe connection successful! Found {len(products.data)} products")
    except Exception as e:
        print(f"✗ Stripe connection failed: {str(e)}")

async def test_supabase():
    print("Testing Supabase connection...")
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        # First just try a simple health check
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{url}/health",
                headers={
                    "apikey": key
                }
            )
            
        if response.status_code == 200:
            print("✓ Supabase health check successful!")
            
            # Then try a simple query that doesn't rely on policies
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{url}/rest/v1/subscription_plans?select=id,name",
                    headers={
                        "apikey": key,
                        "Authorization": f"Bearer {key}"
                    }
                )
                
            if response.status_code == 200:
                print(f"✓ Supabase data query successful! Found subscription plans: {response.json()}")
            else:
                print(f"✗ Supabase data query failed: {response.status_code} {response.text}")
        else:
            print(f"✗ Supabase health check failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"✗ Supabase connection failed: {str(e)}")

async def main():
    test_pinecone()
    print()
    test_gemini()
    print()
    test_stripe()
    print()
    await test_supabase()

if __name__ == "__main__":
    asyncio.run(main())