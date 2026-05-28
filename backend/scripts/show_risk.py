"""Print live risk score and dashboard summary."""
import asyncio
import httpx


async def main():
    from app.main import app
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/risk/summary")
        d = r.json()
        print("=== RISK SUMMARY ===")
        print(f"Score: {d['score']}  Level: {d['level']}")
        print("Components:")
        for comp in d["components"]:
            print(
                f"  {comp['name']:<25} score={comp['score']:>6}  "
                f"weight={comp['weight']}  weighted={comp['weighted']:>5}  [{comp['note']}]"
            )

        r2 = await c.get("/api/dashboard/summary")
        d2 = r2.json()
        print("\n=== DASHBOARD SUMMARY ===")
        print(f"Vessels:         {d2['vessels']['total']:,}")
        print(f"Port calls:      {d2['port_calls']['total']}")
        print(f"AtoN faults:     {d2['aton_faults']['total']} total, {d2['aton_faults']['open']} open")
        print(f"Winter:          {d2['winter_navigation']['active_icebreakers']} active icebreakers, {d2['winter_navigation']['active_dirways']} dirways")
        print(f"Risk:            {d2['risk']['score']} ({d2['risk']['level']})")


if __name__ == "__main__":
    asyncio.run(main())
