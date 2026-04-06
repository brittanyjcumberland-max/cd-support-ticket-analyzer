"""One-time script to generate tickets.csv with 100 realistic fake airline support tickets."""
import csv
import random
import uuid

random.seed(42)

categories = [
    "lost baggage",
    "flight delay",
    "cancellation",
    "seat issue",
    "refund request",
    "app issue",
    "check-in problem",
]

# Weighted distribution so dataset feels realistic
category_weights = [18, 22, 15, 10, 16, 10, 9]

lost_baggage_descriptions = [
    "My bag never showed up on the carousel at JFK. Waited 2 hours. Nobody helped me. I had important medication in that bag!!",
    "Flew in from London Heathrow yesterday and my suitcase is completely missing. Filed a report at the counter but no one has called me back.",
    "This is absolutely ridiculous. My luggage has been 'delayed' for 4 days now. I'm on a business trip and have NO clothes. I need answers NOW.",
    "My bag arrived but the handle is completely broken and there's a big scratch across the side. This was a brand new Samsonite bag.",
    "Both of my checked bags are missing after my connecting flight through Chicago. The agent at the desk just shrugged and gave me a form.",
    "Lost bag on flight AA203. Tag number is still attached. I've called 3 times and keep getting transferred. This is insane.",
    "Arrived in Miami but my stroller never came out. Traveling with a toddler and this is a nightmare. Please help urgently.",
    "My bag was delivered to the wrong address by your courier. Someone else's address was on the delivery slip. How does that even happen?",
    "Still waiting for my bag from my flight 6 days ago. The tracking system just says 'in transit.' I've been buying clothes every day.",
    "Bag came back with broken zipper and my laptop inside is now damaged. I want to know what you're going to do about this.",
]

flight_delay_descriptions = [
    "My flight was delayed 4 hours and I missed my connecting flight to Rome. Now I'm stuck in Frankfurt with no hotel and no help from gate staff.",
    "3 hour delay with zero communication. We sat on the tarmac and nobody told us anything. The wifi didn't even work to look things up.",
    "Flight delayed AGAIN. This is the third time in two months on this route. I'm a Gold member and this is how you treat loyal customers?",
    "2.5 hour delay caused me to miss my daughter's graduation ceremony. I want to know what compensation I'm entitled to.",
    "Gate agent told us 20 min delay. Then 40. Then 2 hours. Then just... nothing. Had to figure out a hotel on my own last minute.",
    "Delayed 6 hours due to 'mechanical issues.' We were never given food vouchers even though the delay was the airline's fault.",
    "The delay was so long my car rental reservation expired. Now I have to pay $80 extra. Who's going to reimburse me for that?",
    "Flight from Denver to Seattle delayed almost 5 hours. Weather was clear. Still not clear why this happened and no one explained.",
    "I understand delays happen but the COMPLETE lack of updates is infuriating. Not one announcement for 3 hours. This is unacceptable.",
    "Missed an important client meeting because of a 3hr delay that wasn't weather-related. I need a written explanation for my employer.",
    "Delay pushed my arrival past midnight and there were no more connecting options. Slept in the airport. Zero assistance offered.",
    "Short 45 minute delay but it caused a ripple effect on my whole day. Missed my medical appointment. Please advise on compensation.",
]

cancellation_descriptions = [
    "My flight was cancelled 30 minutes before boarding and they rebooked me on a flight that's 2 days later. That does NOT work for me.",
    "Flight cancelled due to 'operational reasons' — whatever that means. I've been on hold for 2 hours trying to get a refund.",
    "Cancelled at 5am the morning of my flight. No hotel, no alternate flight, nothing. Had to book on another airline for $600 more.",
    "Got a text cancellation at midnight. I was already at the airport hotel. The rebooking options are all terrible.",
    "My return flight was cancelled and the agent told me the next available seat is in 4 days. I have work. I can't stay 4 more days.",
    "Third cancellation this month on this route. I've lost faith completely. I want a full refund for all future bookings I have.",
    "Cancelled flight, got rebooked automatically but the new flight has a 9-hour layover. Not acceptable. Need a direct flight.",
    "Flight was cancelled but the website is still showing it as 'on time.' Your systems are completely broken.",
]

seat_issue_descriptions = [
    "I paid $65 extra for an aisle seat and was moved to a middle seat with zero notice or refund. I want my money back.",
    "The seat in front of me was completely broken and kept falling back into my lap the entire 8-hour flight.",
    "Booked seats together with my wife months ago. At check-in we were separated by 10 rows. Totally unacceptable on a 5-hour flight.",
    "My seat's armrest is broken. Tray table was also stuck. The seat light didn't work. I paid for business and got economy-level experience.",
    "Assigned exit row but at the gate they gave it to someone else. I'm 6'4 and specifically need that extra legroom.",
    "The person next to me was extremely ill and coughing the entire 7-hour flight. Crew refused to reseat me even when I asked nicely.",
    "Paid for extra legroom seat and when I got on the plane, there was a wall in front of it. Not extra legroom at all.",
    "Seat recline was completely broken for a red-eye flight. No one fixed it. Sleep was impossible.",
    "Family of 4 separated across plane on an international flight. Kids ages 6 and 9. Staff were unhelpful and rude about it.",
    "Booked window seat for my daughter who gets motion sick. They moved us at the gate to a middle of the row. She was sick the whole flight.",
]

refund_descriptions = [
    "I cancelled my ticket within 24 hours of booking and I'm told I can't get a refund, only a travel credit. That is against the law.",
    "Waiting 8 weeks for a refund on a cancelled flight. Keep getting told 'it's being processed.' This is now a dispute with my credit card.",
    "The refund I received was $214 less than what I paid. No explanation of the difference. Please explain or refund the rest.",
    "I was denied boarding because of an overbooking situation and now getting told the refund takes 60-90 days. That's ridiculous.",
    "Used travel credit that was about to expire. Flight was then cancelled by airline. Now being told original credit can't be refunded.",
    "Bought trip insurance but the claim process on your website is completely broken. Submit button does nothing.",
    "My refund was processed but the amount went back to an expired card. Now no one seems to know where the money went.",
    "Canceled due to medical emergency with documentation. Being told the ticket is non-refundable anyway. That can't be right.",
    "Asked for refund to original payment method, got a voucher instead. I didn't ask for a voucher. Please fix this.",
]

app_descriptions = [
    "The app keeps crashing when I try to check in for my flight tomorrow. I've reinstalled it twice already.",
    "Boarding pass won't load in the app. I'm at the airport right now and the wifi here is bad. This is really stressful.",
    "Tried to upgrade my seat through the app and it charged my card twice. Two separate $89 charges.",
    "The app shows my flight is delayed but the airport board shows on time. Which one is correct?? Very confusing.",
    "Apple Wallet integration is broken. My boarding pass won't save. Have to screenshot everything like it's 2012.",
    "Can't add my Known Traveler Number through the app. The field just won't accept any input.",
    "App showed my gate as B12. I went to B12 and the flight was gone. Gate had changed and app never updated.",
    "Every time I try to view my trip, it logs me out. Very frustrating when I'm trying to travel.",
    "The in-app chat support connected me to a bot that couldn't understand anything I said. Completely useless.",
    "Tried to book a flight on the app, it froze on the payment screen. Card was charged but no confirmation received.",
]

checkin_descriptions = [
    "Online check-in closed 45 minutes before it said it would. Had to pay $35 bag drop fee at the airport that I shouldn't have had to.",
    "Checked in online but at the airport they had no record of my check-in. Had to start over and almost missed my flight.",
    "Your kiosks at LAX were ALL broken or out of paper. Line for agents was 45 minutes long. Nearly missed my flight.",
    "The system wouldn't let me check in because it said my name didn't match — but my passport and ticket are IDENTICAL.",
    "Tried to check in online but TSA PreCheck wasn't showing up on my boarding pass. This happens every single time.",
    "Check-in opened 24 hours before my international flight but the website gave error 500 the entire time.",
    "Bag drop queue took over an hour. Only 2 agents working for a full 737. Completely understaffed.",
    "Checked in, printed boarding pass, but the barcode wouldn't scan at security. Had to get a replacement and almost missed my connection.",
    "Mobile check-in not working for group bookings. Had to check in separately for each member which split up our seats.",
]

description_pools = {
    "lost baggage": lost_baggage_descriptions,
    "flight delay": flight_delay_descriptions,
    "cancellation": cancellation_descriptions,
    "seat issue": seat_issue_descriptions,
    "refund request": refund_descriptions,
    "app issue": app_descriptions,
    "check-in problem": checkin_descriptions,
}

resolution_time_ranges = {
    "lost baggage": (12, 120),
    "flight delay": (1, 24),
    "cancellation": (2, 72),
    "seat issue": (1, 12),
    "refund request": (24, 720),
    "app issue": (0.5, 8),
    "check-in problem": (0.5, 6),
}

first_contact_rates = {
    "lost baggage": 0.25,
    "flight delay": 0.55,
    "cancellation": 0.35,
    "seat issue": 0.65,
    "refund request": 0.30,
    "app issue": 0.70,
    "check-in problem": 0.72,
}

selected_categories = random.choices(categories, weights=category_weights, k=100)

rows = []
for i, cat in enumerate(selected_categories):
    ticket_id = f"TKT-{1000 + i}"
    desc_pool = description_pools[cat]
    description = random.choice(desc_pool)
    low, high = resolution_time_ranges[cat]
    resolution_time = round(random.uniform(low, high), 1)
    rate = first_contact_rates[cat]
    was_resolved = "yes" if random.random() < rate else "no"
    rows.append([ticket_id, cat, description, resolution_time, was_resolved])

with open("tickets.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["ticket_id", "category", "description", "resolution_time_hours", "was_resolved_first_contact"])
    writer.writerows(rows)

print("Generated tickets.csv with 100 tickets.")
