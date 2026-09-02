KNOWN FIX (sealed): fxn/zeitwerk commit f9b21aa3dbeef14be794ccf534f1a21cb2e004a1.

failing_ref is parent 8100bd18a42c29740e2d30d21b5f68be67f27d1b.

autoload_path_set_by_me_for? treated any Registry.inception?(cpath) as this loader's path. Gem inception leftover JOIN with app-added MyGem::Foo. Reload dropped the app-added same-name constant.

Repair: inception?(cpath, registered_by_loader) returns the path only when the registering loader is this loader.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
