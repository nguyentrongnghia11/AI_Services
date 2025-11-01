from .database.connectRabbitmq import get_rabbitmq_connection
from .services.toxic_detector_service import ToxicDetector
from .services.hint_post_services import get_list_homologous
from .services.encode_post_service import encode_post_content
from .database.connectMongodb import get_database
import aio_pika
import json
import asyncio
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
from pymongo.errors import WriteConcernError, ConnectionFailure 
load_dotenv()

INPUT_EXCHANGE = "toxic-detect-exchange"
INPUT_QUEUE = "toxic-detect-queue"
RESULT_QUEUE = "result-detect-queue"

INPUT_EXCHANGE2 = "hint-post-exchange"
INPUT_QUEUE2 = "hint-post-queue"
RESULT_QUEUE2 = "result-hint-post-queue"

INPUT_EXCHANGE3 = "encode-post-exchange"
INPUT_QUEUE3 = "encode-post-queue"
RESULT_QUEUE3 = "result-encode-post-queue"

async def setup_exchange_and_queue(channel, input_exchange, input_queue, result_queue):
    """Thiết lập Exchange, Input Queue và Binding."""
    exchange = await channel.declare_exchange(
        input_exchange, 
        aio_pika.ExchangeType.DIRECT, 
        durable=True
    )
    
    input_q = await channel.declare_queue(input_queue, durable=True)
    result_q = await channel.declare_queue(result_queue, durable=True)
    
    await input_q.bind(exchange, routing_key=input_queue)
    await result_q.bind(exchange, routing_key=result_queue)
    
    return exchange, input_q, result_q


async def detectToxicConsumer(stop_event):
    """Worker phát hiện ngôn ngữ thù địch (Toxic Detector) - Async version."""
    try:
        connection = await get_rabbitmq_connection()
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        
        exchange, input_q, result_q = await setup_exchange_and_queue(
            channel, INPUT_EXCHANGE, INPUT_QUEUE, RESULT_QUEUE
        )
        
        async def callback(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    data = json.loads(message.body.decode())
                    text = data.get("content", "")
                    comment_id = data.get("_id") or data.get("commentId")
                    print(f"[ToxicDetector] Processing comment {comment_id}: {text[:50]}...")
                    
                    rs = ToxicDetector(input_text=text, prefix='hate-speech-detection')
                    print(f"[ToxicDetector] Result: {rs}")
                    
                    # Update database with the result
                    if comment_id:
                        try:
                            dbs = await get_database()
                            update_result = await dbs["comments"].update_one(
                                {"_id": ObjectId(comment_id)},
                                {"$set": {"isToxic": rs}}
                            )
                            print(f"[ToxicDetector] Updated isToxic={rs} for comment {comment_id}, matched: {update_result.matched_count}")
                        except Exception as db_error:
                            print(f"!!! Error updating database: {db_error}")
                    
                    response = json.dumps({
                        "commentId": comment_id,
                        "text": text, 
                        "result": rs,
                        "isToxic": rs
                    })
                    await exchange.publish(
                        aio_pika.Message(body=response.encode()),
                        routing_key=RESULT_QUEUE
                    )
                    
                except Exception as e:
                    print(f"!!! Error processing message (Toxic Detect): {e}")
                    raise
        
        await input_q.consume(callback)
        
        print(f"Worker Toxic Detector [{INPUT_QUEUE}] đang chạy...")
        
        # Wait until stop event is set
        while not stop_event.is_set():
            await asyncio.sleep(1)
        
        print("Worker Toxic Detector đã dừng hoàn toàn.")

    except Exception as e:
        print(f"Lỗi khởi động Toxic Worker: {e}")


async def hintPostConsumer(stop_event):
    """Worker đề xuất bài viết (Hint Post) - Async version."""
    try:
        connection = await get_rabbitmq_connection()
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        
        exchange, input_q, result_q = await setup_exchange_and_queue(
            channel, INPUT_EXCHANGE2, INPUT_QUEUE2, RESULT_QUEUE2
        )
        
        async def callback(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    post_data = json.loads(message.body.decode())
                    dbs = await get_database()
                    
                    # Fetch all posts asynchronously
                    cursor = dbs["posts"].find({})
                    list_posts = await cursor.to_list(length=None)
                    
                    homologous_posts = get_list_homologous(post=post_data, list_posts=list_posts)
                    response = json.dumps({"status": "success", "homologous_posts": homologous_posts})
                    
                    await exchange.publish(
                        aio_pika.Message(body=response.encode()),
                        routing_key=RESULT_QUEUE2
                    )
                    
                except Exception as e:
                    print(f"!!! Error processing message (Hint Post): {e}")
                    raise
        
        await input_q.consume(callback)
        
        print(f"Worker Hint Post [{INPUT_QUEUE2}] đang chạy...")
        
        while not stop_event.is_set():
            await asyncio.sleep(1)
        
        print("Worker Hint Post đã dừng hoàn toàn.")
        
    except Exception as e:
        print(f"Lỗi khởi động Hint Post Worker: {e}")
        

async def encodePostConsumer(stop_event):
    """Worker tạo vector nhúng (Embeddings) - Async version."""
    try:
        connection = await get_rabbitmq_connection()
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        
        exchange, input_q, result_q = await setup_exchange_and_queue(
            channel, INPUT_EXCHANGE3, INPUT_QUEUE3, RESULT_QUEUE3
        )

        async def callback(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    post = json.loads(message.body.decode())
                
                    content = post.get('content', '') 
                    post_id = post.get('_id')
                    
                    if not post_id or not content:
                        print(f"Bỏ qua tin nhắn thiếu ID/Content: {post}")
                        return

                    dbs = await get_database()
                    embedding_tensor = encode_post_content(content=content) 
                    
                    embedding_list = embedding_tensor.tolist() 
                    print(f"[EncodePost] Generated embedding for post {post_id}")

                    result = await dbs["posts"].find_one_and_update(
                        {"_id": ObjectId(post_id)}, 
                        {"$set": {"embedding": embedding_list}},
                        upsert=True 
                    )
                    
                    print(f"[EncodePost] Updated: {result}")

                    await exchange.publish(
                        aio_pika.Message(
                            body=json.dumps({"id": post_id, "status": "success"}).encode()
                        ),
                        routing_key=RESULT_QUEUE3
                    )
                    
                except Exception as e:
                    print(f"!!! Lỗi xử lý Encode Post: {e}")
                    raise

        await input_q.consume(callback)

        print(f"Worker Encode Post [{INPUT_QUEUE3}] đang chạy...")
        
        while not stop_event.is_set():
            await asyncio.sleep(1)

        print("worker Encode Post đã dừng hoàn toàn.")
        
    except Exception as e:
        print(f"Lỗi khởi động Encode Worker: {e}")
        