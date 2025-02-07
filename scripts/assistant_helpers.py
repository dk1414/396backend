# assistants_helpers.py

def create_chat_thread(client, user_preferences, intent):
    """
    Creates a new Thread using the Assistants API and pre-populates it with two assistant messages.
    
    Args:
        user_demographics (dict): e.g., {"Name": "Alice", "Email": "alice@example.com"}
        user_preferences (list): List of dicts, e.g., [{"preference_key": "budget", "preference_value": "$100-$200"}, ...]
        intent (str): What the user is looking to buy.
        assistant_id (str): The ID of your pre-created Assistant.
    
    Returns:
        thread_id (str): The ID of the newly created thread.
        initial_messages (list): The list of messages that were added.
    """
    # Step 1: Create a new thread.
    thread = client.beta.threads.create()
    thread_id = thread.id

    # Step 2: Prepare the content for the first assistant message.
    preferences_info = "\n".join(
        f"{pref['preference_key']}: {pref['preference_value']}" for pref in user_preferences
    )
    message1_content = (
        f"User Preferences:\n{preferences_info}\n\n"
        f"User Intent: {intent}"
    )

    # Add the first assistant message.
    msg1 = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="assistant",
        content=message1_content
    )

    # Step 3: Add a second assistant message that asks clarifying questions.
    clarifying_questions = (
        "To better assist you, could you please answer a few questions:\n"
        "1. What is your price range?\n"
        "2. Are there any specific brands or features you're looking for?\n"
        "3. Any other details that are important to you?"
    )
    msg2 = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="assistant",
        content=clarifying_questions
    )

    initial_messages = [msg1, msg2]
    return thread_id, initial_messages



class ChatAgent:
    def __init__(self, client, thread_id, assistant_id):
        """
        Initialize with a thread_id (from your shopping session) and assistant_id.
        """
        self.thread_id = thread_id
        self.assistant_id = assistant_id
        self.client = client

    def add_message(self, user_message):
        """
        Adds a new user message to the thread, runs the Assistant, and returns the updated messages.
        
        Args:
            user_message (str): The content of the user’s new message.
            instructions (str): Additional instructions for the Assistant (optional).
        
        Returns:
            messages (list): The updated list of messages from the thread, or a status dict if not completed.
        """
        # Add the user's message to the thread.
        self.client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=user_message
        )
        
        # Create a run on the thread to generate a response from the assistant.
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id
        )
        
        # Check if the run has completed.
        if run.status == "completed":
            response = self.client.beta.threads.messages.list(thread_id=self.thread_id)
            messages = []
            # Iterate over the message objects from the response.
            for msg in response.data:
                text_value = ""
                # Each message's content is a list of items.
                for item in msg.content:
                    if item.type == "text":
                        text_value += item.text.value
                messages.append({
                    "id": msg.id,
                    "role": msg.role,
                    "created_at": msg.created_at,
                    "content": text_value,
                })
            return messages
        else:
            return {"status": run.status}

