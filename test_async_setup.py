"""
Test script to verify async connections work properly.
Run this before starting the full application.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connectMongodb import get_database, close_mongo_client
from app.database.connectRabbitmq import get_rabbitmq_connection, close_rabbitmq_connection


async def test_mongodb():
    """Test async MongoDB connection."""
    print("\n=== Testing MongoDB (motor) ===")
    try:
        db = await get_database()
        # Try a simple operation
        result = await db.command("ping")
        print(f"✅ MongoDB connection successful: {result}")
        
        # Test a query
        count = await db["posts"].count_documents({})
        print(f"✅ Found {count} posts in database")
        
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False


async def test_rabbitmq():
    """Test async RabbitMQ connection."""
    print("\n=== Testing RabbitMQ (aio-pika) ===")
    try:
        connection = await get_rabbitmq_connection()
        print(f"✅ RabbitMQ connection successful: {connection}")
        
        # Create a test channel
        channel = await connection.channel()
        print(f"✅ Channel created: {channel}")
        
        # Declare a test queue
        queue = await channel.declare_queue("test-queue", durable=True)
        print(f"✅ Test queue declared: {queue.name}")
        
        # Clean up
        await queue.delete()
        print("✅ Test queue deleted")
        
        return True
    except Exception as e:
        print(f"❌ RabbitMQ connection failed: {e}")
        return False


async def test_worker_setup():
    """Test that worker setup functions work."""
    print("\n=== Testing Worker Setup ===")
    try:
        from app.consumer import setup_exchange_and_queue
        
        connection = await get_rabbitmq_connection()
        channel = await connection.channel()
        
        exchange, input_q, result_q = await setup_exchange_and_queue(
            channel,
            "test-exchange",
            "test-input-queue",
            "test-result-queue"
        )
        
        print(f"✅ Exchange declared: {exchange.name}")
        print(f"✅ Input queue declared: {input_q.name}")
        print(f"✅ Result queue declared: {result_q.name}")
        
        # Clean up
        await input_q.delete()
        await result_q.delete()
        await channel.close()
        
        return True
    except Exception as e:
        print(f"❌ Worker setup failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("ASYNC REFACTOR VERIFICATION TEST")
    print("=" * 60)
    
    results = {
        "MongoDB": await test_mongodb(),
        "RabbitMQ": await test_rabbitmq(),
        "Worker Setup": await test_worker_setup()
    }
    
    # Cleanup
    print("\n=== Cleanup ===")
    await close_rabbitmq_connection()
    await close_mongo_client()
    print("✅ All connections closed")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test:20s}: {status}")
    
    all_passed = all(results.values())
    print("\n" + ("🎉 ALL TESTS PASSED!" if all_passed else "⚠️  SOME TESTS FAILED"))
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
