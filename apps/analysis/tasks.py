"""
Celery tasks for spending analysis and data visualization.
"""

from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone

from apps.transactions.models import Transaction

from .models import SpendingAnalysis

User = get_user_model()


@shared_task
def generate_weekly_analysis():
    """주간 소비 분석 데이터 생성"""
    today = timezone.now().date()
    # 이번 주 월요일부터 일요일까지
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    users = User.objects.filter(is_active=True)

    for user in users:
        # 해당 기간의 거래내역 집계
        transactions = Transaction.objects.filter(
            user=user,
            transaction_date__date__gte=start_of_week,
            transaction_date__date__lte=end_of_week,
        )

        total_income = (
            transactions.filter(transaction_type="deposit").aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        total_expense = (
            transactions.filter(transaction_type="withdrawal").aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        transaction_count = transactions.count()
        net_amount = total_income - total_expense

        # 분석 데이터 저장 또는 업데이트
        analysis, created = SpendingAnalysis.objects.update_or_create(
            user=user,
            analysis_type="weekly",
            start_date=start_of_week,
            defaults={
                "end_date": end_of_week,
                "total_income": total_income,
                "total_expense": total_expense,
                "net_amount": net_amount,
                "transaction_count": transaction_count,
            },
        )

        print(
            f"Weekly analysis generated for {user.username}: {start_of_week} ~ {end_of_week}"
        )

    return f"Weekly analysis completed for {users.count()} users"


@shared_task
def generate_monthly_analysis():
    """월간 소비 분석 데이터 생성"""
    today = timezone.now().date()
    # 이번 달 1일부터 마지막 날까지
    start_of_month = today.replace(day=1)
    if today.month == 12:
        end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(
            days=1
        )
    else:
        end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    users = User.objects.filter(is_active=True)

    for user in users:
        # 해당 기간의 거래내역 집계
        transactions = Transaction.objects.filter(
            user=user,
            transaction_date__date__gte=start_of_month,
            transaction_date__date__lte=end_of_month,
        )

        total_income = (
            transactions.filter(transaction_type="deposit").aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        total_expense = (
            transactions.filter(transaction_type="withdrawal").aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        transaction_count = transactions.count()
        net_amount = total_income - total_expense

        # 분석 데이터 저장 또는 업데이트
        analysis, created = SpendingAnalysis.objects.update_or_create(
            user=user,
            analysis_type="monthly",
            start_date=start_of_month,
            defaults={
                "end_date": end_of_month,
                "total_income": total_income,
                "total_expense": total_expense,
                "net_amount": net_amount,
                "transaction_count": transaction_count,
            },
        )

        print(
            f"Monthly analysis generated for {user.username}: {start_of_month} ~ {end_of_month}"
        )

    return f"Monthly analysis completed for {users.count()} users"


@shared_task
def generate_user_analysis(user_id):
    """특정 사용자의 분석 데이터 생성 (수동 호출용)"""
    try:
        user = User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        return f"User {user_id} not found"

    today = timezone.now().date()

    # 주간 분석
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    transactions_weekly = Transaction.objects.filter(
        user=user,
        transaction_date__date__gte=start_of_week,
        transaction_date__date__lte=end_of_week,
    )

    total_income_weekly = (
        transactions_weekly.filter(transaction_type="deposit").aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    total_expense_weekly = (
        transactions_weekly.filter(transaction_type="withdrawal").aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    SpendingAnalysis.objects.update_or_create(
        user=user,
        analysis_type="weekly",
        start_date=start_of_week,
        defaults={
            "end_date": end_of_week,
            "total_income": total_income_weekly,
            "total_expense": total_expense_weekly,
            "net_amount": total_income_weekly - total_expense_weekly,
            "transaction_count": transactions_weekly.count(),
        },
    )

    # 월간 분석
    start_of_month = today.replace(day=1)
    if today.month == 12:
        end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(
            days=1
        )
    else:
        end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    transactions_monthly = Transaction.objects.filter(
        user=user,
        transaction_date__date__gte=start_of_month,
        transaction_date__date__lte=end_of_month,
    )

    total_income_monthly = (
        transactions_monthly.filter(transaction_type="deposit").aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    total_expense_monthly = (
        transactions_monthly.filter(transaction_type="withdrawal").aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    SpendingAnalysis.objects.update_or_create(
        user=user,
        analysis_type="monthly",
        start_date=start_of_month,
        defaults={
            "end_date": end_of_month,
            "total_income": total_income_monthly,
            "total_expense": total_expense_monthly,
            "net_amount": total_income_monthly - total_expense_monthly,
            "transaction_count": transactions_monthly.count(),
        },
    )

    return f"Analysis generated for user {user.username}"
