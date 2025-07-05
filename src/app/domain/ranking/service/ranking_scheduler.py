from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from src.app.core.database import SessionLocal
from src.app.domain.ranking.service import ranking_service

scheduler = AsyncIOScheduler()


def refresh_ranking_job():
    print("🕔 랭킹 자동 갱신 시작")

    # 동기 DB 세션
    db: Session = SessionLocal()
    try:
        # 실제 랭킹 갱신
        import asyncio

        asyncio.run(ranking_service.refresh_all_rankings(db))
        print("✅ 랭킹 갱신 완료")
    except Exception as e:
        print(f"❌ 랭킹 갱신 실패: {e}")
    finally:
        db.close()


def start_ranking_scheduler():
    # 실제 운영 시
    # trigger = CronTrigger(hour=19, minute=25)  # 매일 5:00 AM
    # scheduler.add_job(refresh_ranking_job, trigger, id="daily_ranking_refresh")

    # 테스트 용
    scheduler.add_job(refresh_ranking_job, IntervalTrigger(minutes=360))
    scheduler.start()
