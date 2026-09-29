import sqlite3
import sys

def show_runs(con):
    print("id started questions retries cost_usd fail fake")

    for row in con.execute(
        "SELECT id, started_at, n_questions, n_retries_total, "
        "total_cost_usd, fail_rate, use_fake "
        "FROM runs ORDER BY id DESC"
    ):
        print(
            f"{row[0]:>4} {row[1]:>12.1f} {row[2]:>9} "
            f"{row[3]:>7} {row[4]:>9.4f} {row[5]:>4.2f} {row[6]:>4}"
        )

def search_answers(con, pattern):
    rows = con.execute(
        "SELECT id, run_id, retries, question, answer "
        "FROM answers WHERE question LIKE ? ORDER BY id",
        (f"%{pattern}%",),
    )

    for row in rows:
        print(
            f"[#{row[0]} run={row[1]} retries={row[2]}] "
            f"{row[3]} → {row[4][:140]}"
        )

def main():
    con = sqlite3.connect("results.db")

    if len(sys.argv) > 1 and sys.argv[1] == "--runs":
        show_runs(con)
    else:
        pattern = sys.argv[1] if len(sys.argv) > 1 else ""
        search_answers(con, pattern)

if __name__ == "__main__":
    main()

