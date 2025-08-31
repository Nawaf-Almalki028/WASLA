from django.urls import path
from . import views

app_name="dashboard"


urlpatterns = [
    path('', views.dashboard_home_view, name="dashboard_home_view"),
    path('add_hackathon/<str:type>', views.dashboard_add_hackathon_view, name="dashboard_add_hackathon_view"),
    path('hackathon_details/<id>/', views.dashboard_hackathon_details_view, name="dashboard_hackathon_details_view"),
    path('team_details/<team_id>/', views.dashboard_team_details_view, name="dashboard_team_details_view"),
    path('hackathons/', views.dashboard_hackathons_view, name="dashboard_hackathons_view"),
    path('hackathons/delete/<id>', views.dashboard_delete_hackathon_view, name="dashboard_delete_hackathon_view"),
    path('hackathons/update_stage/<id>', views.dashboard_update_hackathon_stage, name="dashboard_update_hackathon_stage"),
    path('hackathons/update_status/<id>', views.dashboard_update_hackathon_status, name="dashboard_update_hackathon_status"),
    path('hackathons/attend/<id>', views.dashboard_attendence_hackathon_view, name="dashboard_attendence_hackathon_view"),
    path('hackathons/start_hackathon/<int:hackathon_id>', views.dashboard_start_hackathon_view, name="dashboard_start_hackathon_view"),
    path('hackathons/edit/<int:hackathon_id>', views.dashboard_edit_hackathon_view, name="dashboard_edit_hackathon_view"),
    path('hackathons/requirements/delete/<id>', views.dashboard_delete_hackathon_requirement_view, name="dashboard_delete_hackathon_requirement_view"),
    path("hackathons/sign_attendence/<int:team_id>", views.dashboard_set_attendance_view, name="dashboard_set_attendance_view"),
    path("hackathons/sign_winners/<int:id>", views.dashboard_sign_winners_view, name="dashboard_sign_winners_view"),
    path('hackathons/track/delete/<id>', views.dashboard_delete_hackathon_track_view, name="dashboard_delete_hackathon_track_view"),
    path('hackathons/team_member/delete/<member_id>', views.dashboard_delete_team_member_view, name="dashboard_delete_team_member_view"),
    path('hackathons/teams/delete/<id>', views.dashboard_delete_team_view, name="dashboard_delete_team_view"),
    path('judges/<hackathon_id>', views.dashboard_judges_view, name="dashboard_judges_view"),
    path('judges/delete/<judge_id>', views.dashboard_delete_judge_view, name="dashboard_delete_judge_view"),
    path('judges/store_notes/<int:team_id>', views.dashboard_judge_store_notes_view, name="dashboard_judge_store_notes_view"),
    path('add_judges/<hackathon_id>', views.dashboard_add_judges_view, name="dashboard_add_judges_view"),
    path('teams/<hackathon_id>', views.dashboard_teams_view, name="dashboard_teams_view"),
    path('teams_requests/', views.dashboard_teams_requests_view, name="dashboard_teams_requests_view"),
    path('particepents/', views.dashboard_particepents_view, name="dashboard_particepents_view"),
    path('ai_feature/<hackathon_id>/', views.dashboard_ai_feature_view, name="dashboard_ai_feature_view"),
    path('payment_completed/', views.payment_completed, name="payment_completed"),
    path('hackathon/teams_requests/accept/<int:team_id>',views.dashboard_accept_team_view, name="dashboard_accept_team_view"),
    path('hackathon/teams_requests/reject/<int:team_id>',views.dashboard_reject_team_view, name="dashboard_reject_team_view"),
    
]