# Getting Started with Mojo: A Practical Introduction

Mojo is a systems programming language built for high-performance AI infrastructure. It combines **Python's familiar syntax** with **systems-level performance**, making it ideal for developers who need both ease-of-use and raw speed.

## Why Mojo?

### 🚀 Standout Features

- **Pythonic Syntax**: If you know Python, you already know most of Mojo. Write code that feels natural and readable.
- **High Performance**: Compiled directly with MLIR, Mojo achieves C/C++-like speeds without sacrificing readability.
- **Memory Safety**: Mojo's ownership system prevents use-after-free, double-free, and memory leak errors—automatically.
- **Python Interoperability**: Seamlessly import Python libraries into Mojo and call Mojo from Python. Best of both worlds.
- **Struct-Based Types**: Everything from `String` to `Int` is a struct, giving you complete control over performance.

## Your First Program

Let's start simple:

```mojo
def main():
    print("Hello, Mojo!")
```

Every Mojo program needs a `main()` function as its entry point. Save this as `hello.mojo` and run it:

```bash
mojo hello.mojo
```

## Variables and Basic Types

Mojo uses Python-like syntax for variables:

```mojo
def main():
    # Type inference or explicit types—both work
    name = "Alice"
    age: Int = 30
    score: Float64 = 95.5
    
    print(f"Name: {name}, Age: {age}, Score: {score}")
```

## Functions with Type Safety

Mojo's `def` allows flexible typing (like Python), but `fn` requires explicit types for high-performance code:

```mojo
# def: Python-style flexibility
def add(a, b):
    return a + b

# fn: Maximum performance
fn multiply(x: Int, y: Int) -> Int:
    return x * y

def main():
    print(add(3, 5))         # Works with any compatible types
    print(multiply(4, 7))    # Type-safe, compiled
```

## Structs: Custom Types with Speed

Define your own data types as structs, combining data and behavior:

```mojo
struct Point:
    var x: Int
    var y: Int
    
    fn __init__(out self, x: Int, y: Int):
        self.x = x
        self.y = y
    
    fn distance_from_origin(self) -> Int:
        return self.x * self.x + self.y * self.y

def main():
    point = Point(3, 4)
    print(f"Point: ({point.x}, {point.y})")
    print(f"Distance²: {point.distance_from_origin()}")
```

## Ownership: Memory Safety Guaranteed

Mojo's ownership system ensures memory is managed safely and efficiently. Each value has one owner:

```mojo
struct String:
    # Mojo automatically ensures this is freed when it goes out of scope
    pass

def main():
    message = "Hello"  # message owns this String
    
    # When main() ends, message is automatically destroyed
    # No garbage collector, no manual cleanup needed
```

This prevents:
- ❌ Use-after-free errors
- ❌ Double-free crashes
- ❌ Memory leaks

## Practical Example: Temperature Converter

Let's combine what we've learned:

```mojo
struct Temperature:
    var celsius: Float64
    
    fn __init__(out self, celsius: Float64):
        self.celsius = celsius
    
    fn to_fahrenheit(self) -> Float64:
        return self.celsius * 9.0 / 5.0 + 32.0
    
    fn to_kelvin(self) -> Float64:
        return self.celsius + 273.15

def main():
    temp = Temperature(25.0)
    
    print(f"{temp.celsius}°C = {temp.to_fahrenheit()}°F")
    print(f"{temp.celsius}°C = {temp.to_kelvin()}K")
```

## What's Next?

Mojo is powerful and has much more to offer:

- **Control Flow**: `if`, `for`, `while` work as expected
- **Traits**: Define interfaces for polymorphic types
- **Vectorization**: Write code that leverages SIMD and GPU acceleration
- **Python Integration**: Call numpy, use ML libraries, and more
- **Advanced Memory Control**: Pointers and unsafe operations when you need them

## Key Takeaway

Mojo gives you the **best of both worlds**: Python's expressiveness with systems-level performance. Start with simple, readable code—and when you need speed, Mojo's type system and compiler have your back.

Happy coding! 🔥
