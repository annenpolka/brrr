public struct Box {
    public init(width: Double = 10) {}
    public init(width: String = "10") {}
}
public func seed() {
    _ = Box()
    _ = Box(width: 10)
    _ = Box(width: "10")
    _ = Box(width: 20)
}
