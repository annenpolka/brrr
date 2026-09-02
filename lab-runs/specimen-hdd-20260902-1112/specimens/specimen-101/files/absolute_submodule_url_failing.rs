// Reduced excerpt of absolute_submodule_url on failing_ref
// src/cargo/sources/git/utils.rs
// 843a683fef61e9b3f9607ab637b72b0774241513
// SCP-like alternative form is serialized as ssh://.

    let absolute_url = match gix::url::parse(gix::bstr::BStr::new(absolute_url.as_ref().as_bytes()))
    {
        Ok(mut url) if url.serialize_alternative_form && url.scheme == gix::url::Scheme::Ssh => {
            url.serialize_alternative_form = false;
            Cow::from(url.to_bstring().to_string())
        }
        _ => absolute_url,
    };

    Ok(absolute_url)
