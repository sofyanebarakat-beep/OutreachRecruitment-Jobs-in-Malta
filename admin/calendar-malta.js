/* Malta holidays, events and content moments — used by Admin › Social Media › Malta holidays & events.
 *
 * kind:
 *   holiday  — Malta public holiday (fixed date, or Good Friday calculated from Easter)
 *   event    — recurring Maltese event; dates change every year → "usually …", confirm before posting
 *   day      — international day that fits a recruitment / study audience
 *   season   — a hiring or study moment for the month (no specific date)
 * Each item: { kind, name, date?, when?, title, subtitle, body, url, tags }
 */
(() => {
  "use strict";

  // Easter Sunday (Gregorian, "Anonymous" algorithm)
  function easter(y) {
    const a = y % 19, b = Math.floor(y / 100), c = y % 100, d = Math.floor(b / 4), e = b % 4, f = Math.floor((b + 8) / 25),
      g = Math.floor((b - f + 1) / 3), h = (19 * a + b - d - g + 15) % 30, i = Math.floor(c / 4), k = c % 4,
      l = (32 + 2 * e + 2 * i - h - k) % 7, m = Math.floor((a + 11 * h + 22 * l) / 451),
      month = Math.floor((h + l - 7 * m + 114) / 31), day = ((h + l - 7 * m + 114) % 31) + 1;
    return new Date(Date.UTC(y, month - 1, day));
  }
  const iso = (d) => d.toISOString().slice(0, 10);
  const addDays = (d, n) => new Date(d.getTime() + n * 864e5);

  // Fixed public holidays: [month, day, name, post]
  const FIXED = [
    [1, 1, "New Year's Day", { t: "Happy New Year {year}!", s: "New year, new opportunities in Malta", b: "Wishing you a happy and successful {year}! 🎉\n\nIf a new job is on your list of resolutions, **Outreach Recruitment** has **{open} open positions** across Malta & Gozo to help you start the year right.", url: "/jobs", tags: "#HappyNewYear #NewYearNewJob #JobsInMalta" }],
    [2, 10, "Feast of St Paul's Shipwreck", { t: "Happy Feast of St Paul's Shipwreck", s: "Il-Festa tan-Nawfraġju ta' San Pawl", b: "Today Malta celebrates the Feast of St Paul's Shipwreck, one of the island's oldest traditions. 🇲🇹 Wishing everyone celebrating a wonderful feast day!", url: "/jobs", tags: "#StPaulsShipwreck #Malta #Valletta" }],
    [3, 19, "Feast of St Joseph", { t: "Happy Feast of St Joseph", s: "Wishing all workers and families a peaceful public holiday", b: "Today is the Feast of St Joseph — the patron saint of workers. 🔨 We'd like to thank every hard-working professional in Malta. Enjoy the public holiday!", url: "/jobs", tags: "#StJoseph #Malta #PublicHoliday" }],
    [3, 31, "Freedom Day", { t: "Happy Freedom Day, Malta!", s: "Jum il-Ħelsien · 31 March", b: "Today Malta marks Freedom Day (Jum il-Ħelsien), commemorating the departure of the last British forces in 1979. 🇲🇹 Happy Freedom Day to all!", url: "/jobs", tags: "#FreedomDay #JumIlHelsien #Malta" }],
    [5, 1, "Workers' Day", { t: "Happy Workers' Day!", s: "Thank you to everyone who keeps Malta working", b: "Today we celebrate every worker in Malta — in hotels, hospitals, construction sites, offices and at sea. 💪 Thank you for your hard work.\n\nLooking for your next role? We have **{open} open positions** waiting for you.", url: "/jobs", tags: "#WorkersDay #MayDay #JobsInMalta" }],
    [6, 7, "Sette Giugno", { t: "Sette Giugno · 7 June", s: "Remembering the 1919 riots and the road to self-government", b: "Today Malta commemorates Sette Giugno, remembering those who lost their lives in the riots of 7 June 1919 — an important step on the road to self-government. 🇲🇹", url: "/jobs", tags: "#SetteGiugno #Malta #History" }],
    [6, 29, "Feast of St Peter & St Paul (L-Imnarja)", { t: "Happy L-Imnarja!", s: "Feast of St Peter & St Paul · 29 June", b: "Today Malta celebrates L-Imnarja, the Feast of St Peter & St Paul — traditionally celebrated with food, folk music and the gathering at Buskett. 🎶 Enjoy the festivities!", url: "/jobs", tags: "#Imnarja #Mnarja #Malta" }],
    [8, 15, "Feast of the Assumption (Santa Marija)", { t: "Happy Santa Marija!", s: "Feast of the Assumption · 15 August", b: "Happy Santa Marija to everyone in Malta & Gozo! ☀️ Enjoy the feasts, the fireworks and the summer holiday with your loved ones.", url: "/jobs", tags: "#SantaMarija #Malta #Gozo" }],
    [9, 8, "Victory Day", { t: "Happy Victory Day!", s: "Il-Vitorja · Our Lady of Victories · 8 September", b: "Today Malta celebrates Victory Day, remembering the end of the Great Siege of 1565 and the sieges of World War II. 🇲🇹 Happy Victory Day!", url: "/jobs", tags: "#VictoryDay #Vitorja #Malta" }],
    [9, 21, "Independence Day", { t: "Happy Independence Day, Malta!", s: "21 September 1964", b: "Happy Independence Day to all Maltese and to everyone who calls Malta home! 🇲🇹 Proud to help people build their careers on these islands.", url: "/jobs", tags: "#IndependenceDay #Malta #Proud" }],
    [12, 8, "Feast of the Immaculate Conception", { t: "Feast of the Immaculate Conception", s: "Wishing everyone a peaceful public holiday", b: "Today Malta celebrates the Feast of the Immaculate Conception. Wishing all our candidates, clients and partners a peaceful public holiday. ✨", url: "/jobs", tags: "#ImmaculateConception #Malta #PublicHoliday" }],
    [12, 13, "Republic Day", { t: "Happy Republic Day, Malta!", s: "Jum ir-Repubblika · 13 December 1974", b: "Today Malta celebrates Republic Day, marking the day Malta became a republic in 1974. 🇲🇹 Happy Republic Day!", url: "/jobs", tags: "#RepublicDay #Malta" }],
    [12, 25, "Christmas Day", { t: "Merry Christmas from Outreach Recruitment!", s: "Thank you for an amazing year", b: "Merry Christmas to all our candidates, clients and partners! 🎄 Thank you for trusting us this year. We wish you a peaceful Christmas and a successful new year.", url: "/jobs", tags: "#MerryChristmas #Malta #ThankYou" }],
  ];

  // Recurring events — dates vary each year, so they are shown as "usually …"
  const EVENTS = [
    [2, "Malta Carnival", "Usually the 5 days before Ash Wednesday (Valletta, Nadur & across the islands)", { t: "It's Carnival time in Malta! 🎭", s: "Colours, floats and costumes across the islands", b: "Malta's Carnival is here — parades, colourful floats and costumes in Valletta, Nadur and beyond. 🎭 Enjoy the celebrations!", url: "/jobs", tags: "#MaltaCarnival #Karnival #Malta" }, "carnival"],
    [2, "Malta Marathon", "Usually late February / early March", { t: "Good luck to all Malta Marathon runners!", s: "Every step counts — on the road and in your career", b: "Good luck to everyone running the Malta Marathon! 🏃 Just like a career, it's about preparation, persistence and one step at a time.", url: "/jobs", tags: "#MaltaMarathon #Running #Malta" }],
    [4, "Malta International Fireworks Festival", "Usually late April / early May", { t: "Malta lights up the sky ✨", s: "Malta International Fireworks Festival", b: "The Malta International Fireworks Festival is one of the most spectacular events of the year. 🎆 Will you be watching from the Grand Harbour?", url: "/jobs", tags: "#FireworksFestival #Malta #GrandHarbour" }],
    [6, "Valletta Film Festival", "Usually in June", { t: "Movie nights in Valletta 🎬", s: "Valletta Film Festival", b: "Open-air screenings in Valletta's squares — the Valletta Film Festival is a summer highlight. 🎬 Enjoy the show!", url: "/jobs", tags: "#VallettaFilmFestival #Valletta #Malta" }],
    [6, "Village festa season begins", "Festas run from June to September", { t: "Festa season is here! 🎉", s: "Summer feasts, band marches and fireworks", b: "Festa season has started in Malta & Gozo — band marches, decorations and fireworks every weekend. 🎉 Which village festa is your favourite?", url: "/jobs", tags: "#Festa #MaltaSummer #Malta" }],
    [7, "Malta Jazz Festival", "Usually in July (Valletta)", { t: "Jazz by the Grand Harbour 🎷", s: "Malta Jazz Festival", b: "The Malta Jazz Festival brings international artists to Valletta's harbour every summer. 🎷 Enjoy the music!", url: "/jobs", tags: "#MaltaJazzFestival #Valletta #Malta" }],
    [10, "Notte Bianca", "Usually in early October (Valletta)", { t: "Valletta's night of culture 🌙", s: "Notte Bianca", b: "Notte Bianca turns Valletta into an open-air celebration of art, music and culture for one night. 🌙 Will you be there?", url: "/jobs", tags: "#NotteBianca #Valletta #Malta" }],
    [10, "Birgufest", "Usually in October (Birgu)", { t: "Birgu by candlelight 🕯️", s: "Birgufest", b: "During Birgufest the streets of Birgu are lit by thousands of candles — one of Malta's most beautiful sights. 🕯️", url: "/jobs", tags: "#Birgufest #Birgu #Malta" }],
    [10, "Rolex Middle Sea Race", "Usually in October (starts from the Grand Harbour)", { t: "Fair winds to all Middle Sea Race crews! ⛵", s: "Rolex Middle Sea Race · from the Grand Harbour", b: "Good luck to all the crews starting the Rolex Middle Sea Race from the Grand Harbour! ⛵ Malta's maritime tradition is something we're proud of — and our marine sector is hiring.", url: "/marine-jobs-in-malta", tags: "#MiddleSeaRace #Sailing #MarineJobs" }],
    [12, "Christmas season in Malta", "All December", { t: "The festive season is here 🎄", s: "Christmas cribs, markets and lights across Malta", b: "From the Christmas lights in Valletta to cribs (presepji) in every village, Malta is ready for the festive season. 🎄", url: "/jobs", tags: "#ChristmasInMalta #Malta" }],
  ];

  // International days that suit a recruitment / study audience
  const DAYS = [
    [1, 24, "International Day of Education", { t: "Education opens doors 🎓", s: "International Day of Education", b: "Today is the International Day of Education. 🎓 Thinking of studying in Malta? Our guide explains courses, visas and costs step by step.", url: "/study-in-malta-complete-guide", tags: "#EducationDay #StudyInMalta" }],
    [3, 8, "International Women's Day", { t: "Happy International Women's Day!", s: "Celebrating women at work in Malta", b: "Happy International Women's Day! 💜 We celebrate the women building careers and leading teams across Malta — in every sector.", url: "/jobs", tags: "#IWD #InternationalWomensDay #WomenInWork" }],
    [7, 15, "World Youth Skills Day", { t: "Skills shape your future 🛠️", s: "World Youth Skills Day", b: "Today is World Youth Skills Day. 🛠️ Starting your career? Learn how to write a CV that gets noticed in Malta.", url: "/blog/cv-writing-tips-how-to-get-hired-in-malta", tags: "#WorldYouthSkillsDay #CareerTips" }],
    [10, 10, "World Mental Health Day", { t: "Your wellbeing matters 💚", s: "World Mental Health Day", b: "Today is World Mental Health Day. 💚 A healthy workplace starts with people who feel supported — take a moment for yourself and your team today.", url: "/jobs", tags: "#WorldMentalHealthDay #Wellbeing #WorkLife" }],
  ];

  // Hiring / study moments of each month (no fixed date)
  const SEASONS = {
    1: ["New year, new job", { t: "New year, new career?", s: "January is one of the busiest months for job hunting", b: "Many people start the year looking for a new challenge. 🚀 Update your CV and explore **{open} open positions** in Malta.", url: "/jobs", tags: "#NewYearNewJob #JobsInMalta" }],
    3: ["Summer hiring starts (hospitality & tourism)", { t: "Summer season hiring has started ☀️", s: "Hospitality & tourism roles in Malta", b: "Hotels, restaurants and tourism businesses are already hiring for the summer. ☀️ Get ahead — browse hospitality jobs now.", url: "/hospitality-jobs-in-malta", tags: "#HospitalityJobs #SummerJobs #JobsInMalta" }],
    4: ["Employers: plan your summer staffing", { t: "Employers: is your summer team ready?", s: "Plan seasonal staffing before the rush", b: "Peak season comes fast. Planning your summer staffing now means less stress in June. 📅 Tell us who you need — we'll handle the search.", url: "/employers", tags: "#HiringInMalta #SeasonalStaff #Employers" }],
    6: ["Graduates entering the job market", { t: "Congratulations, graduates! 🎓", s: "Ready for your first job in Malta?", b: "Congratulations to everyone graduating this year! 🎓 Ready for your first role? Here's how to make your CV stand out.", url: "/blog/tailor-your-cv-for-jobs-in-malta", tags: "#Graduates #FirstJob #CareerTips" }],
    8: ["Study in Malta: academic year starts soon", { t: "Starting your studies in Malta?", s: "Get ready for the new academic year", b: "The new academic year is around the corner. 📚 Make sure your visa, accommodation and budget are ready.", url: "/malta-student-visa-complete-guide", tags: "#StudyInMalta #InternationalStudents" }],
    9: ["Back to work & back to school", { t: "September: time for a fresh start", s: "Back to work, back to school — and new opportunities", b: "September feels like a new beginning. 🍂 If you're thinking about a career move, now is a great time — new roles are added every week.", url: "/jobs", tags: "#NewStart #JobsInMalta" }],
    10: ["Employers: Christmas staffing", { t: "Christmas staffing? Start now 🎄", s: "Retail, hospitality & logistics peak in December", b: "December is one of the busiest months for retail, hospitality and logistics. Secure your festive-season staff early. 📦", url: "/employers", tags: "#HiringInMalta #ChristmasStaff #Employers" }],
    11: ["Year-end career review", { t: "Is next year your year for a new job?", s: "Review your goals before the year ends", b: "Before the year ends, take 10 minutes to review your career goals. 📝 What would make next year better? We can help you find the right next step.", url: "/jobs", tags: "#CareerGoals #JobsInMalta" }],
  };

  // Items for a month (1-12) of a given year, sorted: dated first, then undated.
  function forMonth(year, month) {
    const out = [];
    for (const [m, d, name, p] of FIXED) if (m === month) out.push({ kind: "holiday", name, date: `${year}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`, ...p });
    const gf = addDays(easter(year), -2);
    if (gf.getUTCMonth() + 1 === month) out.push({ kind: "holiday", name: "Good Friday", date: iso(gf),
      t: "Good Friday", s: "Wishing everyone a peaceful Easter weekend",
      b: "Today is Good Friday, a public holiday in Malta. Wishing everyone a peaceful and reflective Easter weekend. 🕊️", url: "/jobs", tags: "#GoodFriday #Easter #Malta" });
    const ez = easter(year);
    if (ez.getUTCMonth() + 1 === month) out.push({ kind: "day", name: "Easter Sunday", date: iso(ez),
      t: "Happy Easter!", s: "From all of us at Outreach Recruitment", b: "Happy Easter to all our candidates, clients and partners! 🐣 Enjoy the time with family and friends — and don't forget the figolli!", url: "/jobs", tags: "#HappyEaster #Figolli #Malta" });
    const ash = addDays(ez, -46);
    for (const [m, name, when, p, special] of EVENTS) {
      let mm = m, w = when;
      if (special === "carnival") { const start = addDays(ash, -5); mm = start.getUTCMonth() + 1; w = `${year}: ${iso(start)} to ${iso(addDays(ash, -1))} (the 5 days before Ash Wednesday) — confirm local programme`; }
      if (mm === month) out.push({ kind: "event", name, when: w, ...p });
    }
    for (const [m, d, name, p] of DAYS) if (m === month) out.push({ kind: "day", name, date: `${year}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`, ...p });
    if (SEASONS[month]) { const [name, p] = SEASONS[month]; out.push({ kind: "season", name, when: "Any day this month", ...p }); }
    return out.map((x) => ({ ...x, title: x.t, subtitle: x.s, body: x.b }))
      .sort((a, b) => (a.date && b.date ? a.date.localeCompare(b.date) : a.date ? -1 : b.date ? 1 : 0));
  }

  window.MaltaCalendar = { forMonth, easter };
})();
