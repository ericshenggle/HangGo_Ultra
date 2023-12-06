from ars.commission.views import commission_views, type_views, commission_change_views, apply_views, comment_views, \
    condition_views, user_commissions, recommend_views
from django.urls import path

urlpatterns = [
    path('commission/search/all/', commission_views.Commission_All_View.as_view()),
    path('commission/search/all/Admin/', commission_views.Commission_All_Admin_View.as_view()),
    path('commission/search/history/', commission_views.Commission_History_View.as_view()),
    path('commission/search/recommend/', recommend_views.recommend_View.as_view()),
    path('commission/detail/', commission_views.Commission_One_View.as_view()),

    path('condition/commissions/', condition_views.condition_Top_View.as_view()),

    path('commission/search/specific/<sort>/', type_views.Commission_Sort_View.as_view()),
    path('commission/sort/', type_views.Commission_Type_View.as_view()),
    path('commission/sort/<id>/', type_views.Commission_Type_One_View.as_view()),

    path('commission/publish/', commission_change_views.Commission_Publish_view.as_view()),
    path('commission/check/<Status>/', commission_change_views.Commission_Check_view.as_view()),
    path('commission/check/', commission_change_views.Commission_Change_view.as_view()),

    path('commission/apply/', apply_views.Commission_Apply_View.as_view()),
    path('commission/applied/<Status>/', apply_views.Commission_Apply_Status_View.as_view()),
    path('commission/drop/', apply_views.Commission_Drop_View.as_view()),
    path('commission/terminate/', apply_views.Commission_Terminate_View.as_view()),
    path('commission/finish/', apply_views.Commission_Finish_View.as_view()),

    path('commission/score/', comment_views.Commission_Score_View.as_view()),
    path('commission/comment/', comment_views.Commission_Comment_View.as_view()),
    path('commission/comment/<id>/', comment_views.Commission_Comment_One_View.as_view()),
    path('comment_commissions/<com_id>/', comment_views.Commission_Comment_Com_View.as_view()),
    path('comment_users/', comment_views.Commission_Comment_User_View.as_view()),

    path('user_create_commissions/<id>/', user_commissions.User_Create_Commissions.as_view()),
    path('user_create_commissions_self/<id>/', user_commissions.User_Create_Commissions_Self.as_view())
]
