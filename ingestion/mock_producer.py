import json
from kafka import KafkaProducer
import time
import random
import uuid

# ==========================================
# 1. CONFIGURATION
# ==========================================
KAFKA_TOPIC = 'employee_live_chat'

# ==========================================
# 2. INITIALIZE KAFKA PRODUCER
# ==========================================
# We connect to localhost:9092, which is the port we opened in docker-compose.
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print(f"🚀 Connected to Kafka! Generating live mock data...")
print(f"📡 Forwarding to topic: '{KAFKA_TOPIC}'...\n")

# Mock data templates to simulate a real company
departments = ["Engineering", "HR", "IT Support", "Sales"]
issues = [
    "The main database is experiencing high latency.",
    "How do I reset my VPN password?",
    "Deployment to production failed with error code 502.",
    "Is the cafeteria serving pizza today?",
    "Customer X is asking for a refund on their latest invoice.",
    "I cannot connect to the internal company portal.",
    "We just closed the massive Q3 deal with the new client!"
]

# ==========================================
# 3. THE LIVE STREAM LOOP
# ==========================================
try:
    while True: # This loop runs forever until you stop it!
        
        # Package our simulated data into a clean dictionary
        document = {
            "id": str(uuid.uuid4()),
            "department": random.choice(departments),
            "text": random.choice(issues),
            "timestamp": time.time()
        }
        
        # Send the data to our Kafka waiting room!
        producer.send(KAFKA_TOPIC, document)
        producer.flush() # Ensure it gets sent immediately
        
        print(f"✅ Sent to Kafka: [{document['department']}] {document['text'][:40]}...")
        
        # Wait randomly between 2 to 5 seconds before sending the next one
        time.sleep(random.uniform(2.0, 5.0))

except KeyboardInterrupt:
    print("\n🛑 Shutting down the producer stream.")
    producer.close()