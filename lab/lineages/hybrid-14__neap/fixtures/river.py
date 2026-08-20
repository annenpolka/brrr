def bar_color(flow_score):
    if flow_score > 0.2:
        return "flow"
    elif flow_score < -0.2:
        return "drift"
    return "still"
