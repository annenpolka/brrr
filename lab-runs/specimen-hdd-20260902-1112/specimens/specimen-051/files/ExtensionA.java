public abstract class A {
    public abstract static class B {}

    public abstract static class Params implements ValueSourceParameters {
        @Nested
        public abstract Property<B> getB();
    }

    public abstract static class V implements ValueSource<String, Params> {}

    private final Provider<String> calculated;

    @Inject
    public A(ProviderFactory providers) {
        var source = providers.of(V.class, it -> {
            it.getParameters().getB().set(getB());
        });
        this.calculated = source;
    }

    @Nested
    public abstract B getB();

    public Provider<String> getCalculated() {
        return calculated;
    }
}
