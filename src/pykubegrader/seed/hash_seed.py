import hashlib

def hash_to_seed(input_string):
    """
    Hash a string into a small integer seed less than 500.
    
    Parameters:
        input_string (str): The string to hash.
    
    Returns:
        int: A seed value (0 <= seed < 500).
    """
    # Ensure the input is a string
    input_string = str(input_string)
    
    # Create a SHA-256 hash of the string
    hash_object = hashlib.sha256(input_string.encode())
    
    # Convert the hash to an integer
    large_number = int.from_bytes(hash_object.digest(), 'big')
    
    # Reduce the number to a value less than 500
    small_seed = large_number % 500
    
    return small_seed