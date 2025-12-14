from django.urls import path
from .views import TestView, chart_schema, upload_chart, list_charts, code_chart

urlpatterns = [
    #### #! DO NOT MODIFY THIS CODE #! ####

    path("test-view/", TestView.as_view(), name="test-view"),
    
    #### #! END OF DO NOT MODIFY THIS CODE #! ####

    path("chart-schema/", chart_schema),

    path("upload-chart/", upload_chart),

    path("charts/", list_charts),

    path("code-chart/", code_chart)

    # Create your urls here.
]


