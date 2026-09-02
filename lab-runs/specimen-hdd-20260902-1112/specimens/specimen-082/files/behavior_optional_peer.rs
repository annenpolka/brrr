# Reduced excerpt of Behavior flags on failing_ref
# src/install_types/resolver_hooks.rs

impl Behavior {
    /// Peer-optionals are reported separately.
    pub fn is_optional(self) -> bool {
        self.contains(Self::OPTIONAL) && !self.contains(Self::PEER)
    }
    pub fn is_optional_peer(self) -> bool {
        self.contains(Self::OPTIONAL) && self.contains(Self::PEER)
    }
    pub fn is_peer(self) -> bool {
        self.contains(Self::PEER)
    }
}
