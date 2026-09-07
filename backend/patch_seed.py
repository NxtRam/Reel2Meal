with open("app/utils/seed_reels.py", "r") as f:
    content = f.read()

# Replace the slow delete with a bulk delete
old_code = """        # Delete existing seed reels to avoid duplicates on re-run
        existing = await db.execute(select(Reel).where(Reel.creator_id == creator_id))
        for r in existing.scalars().all():
            await db.delete(r)
        await db.flush()"""

new_code = """        # Delete existing seed reels to avoid duplicates on re-run
        await db.execute(text("DELETE FROM reels WHERE creator_id = :creator_id"), {"creator_id": creator_id})
        await db.flush()"""

content = content.replace(old_code, new_code)

with open("app/utils/seed_reels.py", "w") as f:
    f.write(content)
