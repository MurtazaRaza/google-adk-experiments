class HelloWorld:
    """A sample class that holds a hello world function."""
    
    def hello_world(self):
        """Returns a hello world message."""
        return "Hello, World!"
    
    def greet(self, name: str = "World") -> str:
        """Returns a personalized greeting.
        
        Args:
            name: The name to greet. Defaults to "World".
            
        Returns:
            A greeting message.
        """
        return f"Hello, {name}!"

