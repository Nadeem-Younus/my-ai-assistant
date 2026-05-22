
# OpenAI Key
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client =   OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

########### Chat #############
# Chat Mode
def chat_mode():
    """Chat with conversation memory"""
    #print_header("CHAT MODE")
    print("Start chatting! Type 'quit', 'exit', 'q' to exit.\n")
    
    # TODO: Create conversation with system prompt
    conversation = [
        {"role": "system", "content": "You are helpful."}
    ]
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye! 👋\n")
            break
        
        if not user_input:
            continue
        
        # TO-DO: Add user message
        conversation.append({"role": "user", "content": user_input})
        
        # TO-DO: Call API
        response = make_api_call(conversation)
        
        print(f"\nAI: {response}\n")
        
        # TO-DO: Add AI response
        conversation.append({"role": "assistant", "content": response})


########### Tool functions #############

# Complete Calculator with Error Handling.
def calculate_safe(expression):
    try:
        expression = str(expression)
        result = eval(expression, {"__builtins__": {}}, {})
        return json.dumps({"success": True, "result": result})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

def web_search(query):
    results = {
        "ai trends": "Latest AI: Advanced reasoning, multimodal models",
        "technology": "Tech news: AI adoption accelerating",
        "email tips": "Email tips: Clear subject, concise content"
    }
    for keyword in results:
        if keyword in query.lower():
            return json.dumps({"results": results[keyword]})
    return json.dumps({"results": f"Info about {query}"})

def analyze_data(data_string, operation):
    data = json.loads(data_string)
    if operation == "sum": result = sum(data)
    elif operation == "average": result = sum(data) / len(data)
    elif operation == "max": result = max(data)
    elif operation == "min": result = min(data)
    else: result = None
    return json.dumps({"result": result})

def get_weather(location):
    """ Mock_weather_tool """
    weather_data = {
        "multan": "Hot , 38C, Sunny ",
        "lahore": "Warm , 32C, Partly ␣ cloudy ",
        "karachi": "Humid , 30C, Overcast "
        }
    return json.dumps({f"weather in {location}": weather_data.get(location.lower(), "Unknown_location")})


# Tool schemas
calculator_tool = {"type": "function", "function": {"name": "calculate", "description": "Do math", "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}}}
web_search_tool = {"type": "function", "function": {"name": "web_search", "description": "Search web", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}}
data_analyzer_tool = {"type": "function", "function": {"name": "analyze_data", "description": "Analyze data", "parameters": {"type": "object", "properties": {"data_string": {"type": "string"}, "operation": {"type": "string", "enum": ["sum", "average", "max", "min"]}}, "required": ["data_string", "operation"]}}}
weather_tool = {"type": "function", "function": {"name": "get_weather", "description": "Get_current_weather", "parameters": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}}}

#print("✅ Tools loaded!")

import json

class MultiToolAssistant:
    """
    COMPLETE assistant with all tools.
    Tracks usage and handles errors.
    """
    
    def __init__(self):
        self.tools = [calculator_tool, web_search_tool, data_analyzer_tool, weather_tool]
        self.functions = {
            "calculate": calculate_safe,
            "web_search": web_search,
            "analyze_data": analyze_data,
            "get_weather": get_weather
        }
        self.tool_usage = {name: 0 for name in self.functions.keys()}
    
    def ask(self, question):
        """Ask a question and get answer (using tools if needed)"""
        print(f"❓ Question: {question}\n")
        
        messages = [{"role": "user", "content": question}]
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=self.tools
        )
        
        response_message = response.choices[0].message
        
        if not response_message.tool_calls:
            return response_message.content
        
        messages.append(response_message)
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Track usage
            self.tool_usage[function_name] += 1
            
            print(f"🔧 Using {function_name}...")
            
            result = self.functions[function_name](**function_args)
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
        
        final_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        print()
        return final_response.choices[0].message.content
    
    def stats(self):
        """Show usage statistics"""
        print("\n📊 Tool Usage Statistics:")
        print("=" * 40)
        for tool, count in self.tool_usage.items():
            print(f"  {tool}: {count} calls")
        print("=" * 40)

# Create assistant


############## EnhancedEmailWriter class ################
class EnhancedEmailWriter:
    """
    COMPLETE email writer that can research topics.
    """
    
    def __init__(self):
        self.tools = [web_search_tool]
        self.functions = {"web_search": web_search}
    
    def write(self, description, tone="professional"):
        print(f"\n📧 Writing email: {description}")
        print(f"   Tone: {tone}\n")
        
        system_prompt = f"""You are a professional email writer.
        Write in a {tone} tone.
        Tone rules:
        - casual: friendly, simple, conversational
        - professional: business-like, clear, structured
        - formal: strict, respectful, corporate language
        
        If you need current information, use web_search.
        Include subject, greeting, body, closing."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Write email: {description}"}
        ]
        
        # First API call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=self.tools
        )
        
        response_message = response.choices[0].message
        
        # Check if AI wants to research
        if response_message.tool_calls:
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"🔍 Researching: {function_args.get('query', 'N/A')}")
                
                result = self.functions[function_name](**function_args)
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
            
            # Get final email with research
            final_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            
            return final_response.choices[0].message.content
        
        return response_message.content

    '''print("\n" + "=" * 70)
    print("📧 EMAIL")
    print("=" * 70)
    #print(email)
    print("=" * 70)
    '''

############# SmartSummarizer class ###########
"""COMPLETE summarizer with analytics."""
class SmartSummarizer:
    """
    COMPLETE summarizer with detailed analytics.
    """
    
    def summarize(self, text, style="short"):
        print(f"\n📝 Summarizing ({style} style)...\n")
        
        # Analytics
        word_count = len(text.split())
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        
        # Style instructions
        styles = {
            "short": "1-2 sentences",
            "medium": "A paragraph (3-4 sentences)",
            "detailed": "Multiple paragraphs"
        }
        
        # Get summary
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Summarize as {styles.get(style, styles['short'])}"},
                {"role": "user", "content": f"Summarize:\n{text}"}
            ],
            temperature=0.3
        )
        
        summary = response.choices[0].message.content
        summary_words = len(summary.split())
        reduction = ((word_count - summary_words) / word_count * 100)
        
        # Display
        print("=" * 70)
        print("📊 SUMMARY ANALYSIS")
        print("=" * 70)
        print(f"Original: {word_count} words, ~{sentence_count} sentences")
        print(f"Summary: {summary_words} words")
        print(f"Reduction: {reduction:.1f}%")
        print(f"Style: {style.title()}")
        print()
        print("-" * 70)
        print("SUMMARY")
        print("-" * 70)
        print(summary)
        print("-" * 70)


######## MultiCapabilityAssistant class ##########

class MultiCapabilityAssistant:
    """
    COMPLETE multi-capability assistant.
    
    Features:
    - Chat with memory
    - Enhanced email writer (with research)
    - Smart summarizer (with analytics)
    - Calculator, web search, data analysis tools
    
    This is your PROJECT TEMPLATE - customize it!
    """
    
    def __init__(self):
        # All tools
        self.tools = [calculator_tool, web_search_tool, data_analyzer_tool, weather_tool]
        self.functions = {
            "calculate": calculate_safe,
            "web_search": web_search,
            "analyze_data": analyze_data,
            "get_weather": get_weather
        }
        
        # Sub-components
        self.email_writer = EnhancedEmailWriter()
        self.summarizer = SmartSummarizer()
        
        print("=" * 77)
        print("✅ Multi-Capability Assistant initialized!")
        print("   Capabilities: Chat, Email, Summarize, Calculate, Search, Analyze, Weather\n")
        print("=" * 77)

    def extract_tone(self, request):
        request_lower = request.lower()

        if "casual" in request_lower:
            return "casual"
        elif "formal" in request_lower:
            return "formal"
        elif "professional" in request_lower:
            return "professional"
        else:
            return "professional"
        
    def route_request(self, request):
        """Decide which capability to use"""
        request_lower = request.lower()
        
        if any(word in request_lower.strip() for word in ['email', 'write to', 'compose']):
            return 'email'
        
        elif any(word in request_lower.strip() for word in ['summarize', 'summary']):
            return 'summarize'
        
        elif any(word in request_lower.strip() for word in ['calculate', 'math', 'average', '+', '-', '*', '/']):
            return 'tools'
        
        elif any(word in request_lower.strip() for word in "+-*/") and any(ch.isdigit() for ch in request_lower.strip()):
            return "tools"
    
        elif any(word in request_lower.strip() for word in ['analyze', 'data']):
            return 'analyze'
        
        elif any(word in request_lower.strip() for word in ['weather', 'get weather']):
            return 'weather'
        
        else:
            return 'general'
    
    def process(self, request):
        """Process any request intelligently"""
        print(f"\n{'=' * 70}")
        print(f"📥 Request: {request}")
        print("=" * 70)
        
        capability = self.route_request(request)
        print(f"🎯 Using: {capability.upper()}\n")
        
        if capability == 'email':
            tone = self.extract_tone(request)
            # remove tone keywords from actual email description
            clean_request = request.replace("casual", "").replace("formal", "").replace("professional", "")
            return self.email_writer.write(clean_request.strip(), tone)
        
        elif capability == 'summarize':
            return "Please provide text to summarize."
        
        elif capability == 'calculator':
            return self.use_tools(request)
        
        elif capability == 'analyze':
            return self.use_tools(request)
        
        elif capability == 'weather':
            #location = request.replace("weather", "").strip()
            return self.use_tools(request)
        
        else:
            return self.general_assistant(request)
    
    def use_tools(self, query):
        """Use tools to answer query"""
        messages = [{"role": "user", "content": query}]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=self.tools
        )
        
        response_message = response.choices[0].message
        
        if not response_message.tool_calls:
            return response_message.content or "No response generated"
            #return response_message.content

        messages.append(response_message)
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"🔧 Using {function_name}...")
            
            #result = self.functions[function_name](**function_args)
            func = self.functions.get(function_name)

            if not func:
                return json.dumps({"error": f"Unknown tool: {function_name}"})

            result = func(**function_args)
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
        
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        return final_response.choices[0].message.content or "Sorry, I could not generate response."
    
    def general_assistant(self, query):
        """General purpose assistant"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": query}],
            tools=self.tools
        )
        return response.choices[0].message.content

# Create the assistant
assistant = MultiCapabilityAssistant()

while True:
    user_input = input("\n💬 Enter request (or 'exit'): ")

    if user_input.lower() == "exit":
        break

    response = assistant.process(user_input)
    print("\n🤖 RESPONSE:\n", response)