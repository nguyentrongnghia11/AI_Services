from .database.connectRabbitmq import get_rabbitmq_connection
from .services.toxic_detector_service import ToxicDetector
from .services.hint_post_services import get_list_homologous
from .services.encode_post_service import encode_post_content
from .database.connectMongodb import get_database
import pika
import json
import time
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

def setup_exchange_and_queue(channel, input_exchange, input_queue, result_queue):
    channel.exchange_declare(exchange=input_exchange, exchange_type='direct', durable=True)
    channel.queue_declare(queue=input_queue, durable=True)
    channel.queue_declare(queue=result_queue, durable=True)
    
    channel.queue_bind(exchange=input_exchange, queue=input_queue, routing_key=input_queue)
    channel.queue_bind(exchange=input_exchange, queue=result_queue, routing_key=result_queue)


def detectToxicConsumer(stop_event):
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        setup_exchange_and_queue(channel, INPUT_EXCHANGE, INPUT_QUEUE, RESULT_QUEUE)
        
        def callback(ch, method, properties, body):
            try:
                data = json.loads(body)
                text = data.get("text", "")
                print (text)
                rs = ToxicDetector(input_text=text, prefix='hate-speech-detection')
                print (rs)
                response = json.dumps({"text": text, "result": rs})

                channel.basic_publish(INPUT_EXCHANGE, RESULT_QUEUE, body=response)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f"!!! Error processing message (Toxic Detect): {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=INPUT_QUEUE, on_message_callback=callback)
        
        print(f"Worker Toxic Detector [{INPUT_QUEUE}] đang chạy...")
        while not stop_event.is_set():
            connection.process_data_events(time_limit=1)
        
        channel.close(); connection.close()
        print("Worker Toxic Detector đã dừng hoàn toàn.")

    except Exception as e:
        print(f"Lỗi khởi động Toxic Worker: {e}")


def hintPostConsumer(stop_event):
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        setup_exchange_and_queue(channel, INPUT_EXCHANGE2, INPUT_QUEUE2, RESULT_QUEUE2)
        
        def callback(ch, method, properties, body):
            try:
                post_data = json.loads(body)
                dbs = get_database()
                list_posts = list(dbs["posts"].find({})) 
                
                homologous_posts = get_list_homologous(post=post_data, list_posts=list_posts)
                response = json.dumps({"status": "success", "homologous_posts": homologous_posts})
                
                channel.basic_publish(exchange=INPUT_EXCHANGE2, routing_key=RESULT_QUEUE2, body=response)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f"!!! Error processing message (Hint Post): {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=INPUT_QUEUE2, on_message_callback=callback)
        
        print(f"Worker Hint Post [{INPUT_QUEUE2}] đang chạy...")
        while not stop_event.is_set():
            connection.process_data_events(time_limit=1)
        
        channel.close(); connection.close()
        print("Worker Hint Post đã dừng hoàn toàn.")
        
    except Exception as e:
        print(f"Lỗi khởi động Hint Post Worker: {e}")
        

def encodePostConsumer(stop_event):
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        setup_exchange_and_queue(channel, INPUT_EXCHANGE3, INPUT_QUEUE3, RESULT_QUEUE3)

        def callback(ch, method, properties, body):
            try:
                post = json.loads(body)
            
                content = post.get('content', '') 
                post_id = post.get('_id')
                
                if not post_id or not content:
                    print(f"Bỏ qua tin nhắn thiếu ID/Content: {post}")
                    return ch.basic_ack(delivery_tag=method.delivery_tag)

                dbs = get_database()
                embedding_tensor = encode_post_content(content=content) 
                
                embedding_list = embedding_tensor.tolist() 
                print (embedding_list)

                result = dbs["posts"].find_one_and_update(
                    {"_id": ObjectId(post_id)}, 
                    {"$set": {"embedding": embedding_list}},
                    upsert=True 
                )
                
                print (result)

                channel.basic_publish(exchange=INPUT_EXCHANGE3, routing_key=RESULT_QUEUE3, body=json.dumps({"id": post_id, "status": "success"}))
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f"!!! Lỗi xử lý Encode Post: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=INPUT_QUEUE3, on_message_callback=callback)

        print(f"Worker Encode Post [{INPUT_QUEUE3}] đang chạy...")
        while not stop_event.is_set():
            connection.process_data_events(time_limit=1)

        channel.close(); connection.close()
        print("worker Encode Post đã dừng hoàn toàn.")
        
    except Exception as e:
        print(f"Lỗi khởi động Encode Worker: {e}")
        