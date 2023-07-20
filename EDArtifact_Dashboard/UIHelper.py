class UIHelper:
    def get_shape(self, start, end, color):
        return {
            "type": "rect",
            "xref": "x",
            "yref": "paper",
            "x0": start,
            "y0": 0,
            "x1": end,
            "y1": 1,
            "fillcolor": color,
            "opacity": 0.2,
            "line": {
                "width": 0,
            },
        }

    def get_current_marker(self, start, end):
        return {
            "type": "rect",
            "xref": "x",
            "yref": "paper",
            "x0": start,
            "y0": 0,
            "x1": end,
            "y1": 1,
            "fillcolor": "#d3d3d3",
            "opacity": 0.5,
            "line": {
                "width": 0,
            },
        }
