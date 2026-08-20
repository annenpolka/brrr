public struct Review {
    public mutating func reopenUnit(id: String, returningToFinal: Bool = true) {}
}
public struct Panel {
    func reopenUnit(id: String) {
        review?.reopenUnit(id: id)
    }
    var review: Review?
}
public func seed(r: inout Review) {
    r.reopenUnit(id: "x")
    r.reopenUnit(id: "x", returningToFinal: true)
}
