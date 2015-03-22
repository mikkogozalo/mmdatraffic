def get_first(sel, xpath, default=None):
    results = sel.xpath(xpath).extract()
    if results:
        return results[0]
    else:
        return default
