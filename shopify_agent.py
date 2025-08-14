from typing import Annotated, Literal, TypedDict
from langgraph.graph import MessagesState, StateGraph
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
import os
from dotenv import load_dotenv
from shopify_tools import SHOPIFY_TOOLS


class AgentState(MessagesState):
    """State for the Shopify agent"""
    pass

def create_shopify_agent(
    openai_api_key: str,

):
    """
    Create a Shopify agent with the specified configuration.
    """
    
    load_dotenv()
    BASE_URL = os.getenv("OPENAI_API_BASE")
    if not BASE_URL:
        raise ValueError("OPENAI_API_BASE environment variable is not set")
    
    # Initialize llm with tools
    llm = ChatOpenAI(
        api_key=openai_api_key,
        model="deepseek/deepseek-chat-v3-0324:free",
        base_url=BASE_URL,
        temperature=0.0
    ).bind_tools(SHOPIFY_TOOLS)
    
    # define agent node
    def agent_node(state: AgentState):
        """Main agent node that processes messages and decides on tool usage"""
        
        messages = state["messages"]
        
        response = llm.invoke(messages)
        
        return {"messages": [response]}
    
    # Creating tool node for executing tools
    tool_node = ToolNode(SHOPIFY_TOOLS)
    
    def should_continue(state: AgentState) -> Literal["tools", "end"]:
        """Determines whether to continue with tool calls or end the conversation"""
        messages = state["messages"]
        last_message = messages[-1] if messages else None
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "end"
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    workflow.set_entry_point("agent")
    
    workflow.add_conditional_edges("agent", should_continue, {
        "tools": "tools",
        "end": "__end__"
    })
    
    workflow.add_edge("tools", "agent")
    
    memory = MemorySaver()
    
    app = workflow.compile(checkpointer=memory)
    
    return app

class ShopifyAgentManager:
    """Helper class to manage the Shopify agent"""

    def __init__(self, openai_api_key: str):
        self.app = create_shopify_agent(
            openai_api_key=openai_api_key,
        )
    
    def chat(self, message: str, thread_id: str="default") -> str:
        """
        Send a message to the agent and get a response.
        
        Args:
            message: User message
            thread_id: Conversation thread ID for memory persistence
        
        Returns:
            Agent's response
        """
        config = {"configurable": {"thread_id": thread_id}}
        
        response = self.app.invoke(
            {"messages": [HumanMessage(content=message)]},
            config=config
        )
        
        return response["messages"][-1].content if response["messages"] else "No response from agent"
    
    def stream_chat(self, message: str, thread_id: str="default"):
        """
        Stream the agent's response for real-time interaction.
        
        Args:
            message: User message
            thread_id: Conversation thread ID for memory persistence
        
       Yields:
            Streaming response chunks
        """
        config = {"configurable": {"thread_id": thread_id}}
        
        for chunk in self.app.stream(
            {"messages": [HumanMessage(content=message)]},
            config=config
        ):
            if "agent" in chunk:
                if "messages" in chunk["agent"]:
                    message = chunk["agent"]["messages"][0]
                    if hasattr(message, "content") and message.content:
                        yield message.content

def main():
    load_dotenv()
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    if not all([OPENAI_API_KEY]):
        print("Please make sure OPENAI_API_KEY is set in the environment variables:")
        return
    
    agent_manager = ShopifyAgentManager(
        openai_api_key=OPENAI_API_KEY,
    )
    
    print("Shopify Agent is ready.")
    print("Running test examples...")
    print()
    
    # Get products
    print("Client: Show me the first 5 products in my store")
    response = agent_manager.chat("Show me the first 5 products in my store")
    print("Agent🤖:", response)
    print()
    
    # Get orders
    print("Client: Who are my recent customers? I want to see their names and emails")
    response = agent_manager.chat("Who are my recent customers? I want to see their names and emails")
    print("Agent🤖:", response)
    print()
    
    # Get specific product
    print("Client: Get details for product with ID 8488292647068")
    response = agent_manager.chat("Get details for product with ID 8488292647068")
    print("Agent🤖:", response)
    print()
    
    print("Exiting program...")
    agent_manager = None

if __name__ == "__main__":
    main()