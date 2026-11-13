// Made by social-robot/tools/make_live_js.py. Do not edit by hand.
// Turns an episode into a YouTube link once it has gone live.
(() => {
  const videos = {
 "2026-11-13": [
  "KSIrdYMZ9Nw",
  "2026-11-13T14:00:00+00:00"
 ],
 "2026-11-17": [
  "rw2U3n3Jjok",
  "2026-11-17T14:00:00+00:00"
 ],
 "2026-11-20": [
  "np-qi8R7QYE",
  "2026-11-20T14:00:00+00:00"
 ],
 "2026-11-24": [
  "ednqpbRAQC8",
  "2026-11-24T14:00:00+00:00"
 ],
 "2026-11-27": [
  "2S-1mJi5QL8",
  "2026-11-27T14:00:00+00:00"
 ],
 "2026-12-01": [
  "X2Gz4a-XogE",
  "2026-12-01T14:00:00+00:00"
 ],
 "2026-12-04": [
  "7pIwULpff6Y",
  "2026-12-04T14:00:00+00:00"
 ],
 "2026-12-08": [
  "SzoJw82j1PY",
  "2026-12-08T14:00:00+00:00"
 ],
 "2026-12-11": [
  "B87Cl7wruOg",
  "2026-12-11T14:00:00+00:00"
 ],
 "2026-12-15": [
  "hM1EfAD66FM",
  "2026-12-15T14:00:00+00:00"
 ],
 "2026-12-18": [
  "7PG6ECqGvps",
  "2026-12-18T14:00:00+00:00"
 ],
 "2026-12-22": [
  "a4DrwyRi4kU",
  "2026-12-22T14:00:00+00:00"
 ],
 "2026-12-25": [
  "xLJMMFJ8KkU",
  "2026-12-25T14:00:00+00:00"
 ],
 "2027-01-01": [
  "b-7Xs55Zb1w",
  "2027-01-01T14:00:00+00:00"
 ],
 "2027-01-27": [
  "TOZXjqH4VO4",
  "2027-01-27T14:00:00+00:00"
 ]
};
  const now = new Date();
  const link = (id, text) => {
    const a = document.createElement('a');
    a.href = 'https://www.youtube.com/watch?v=' + id;
    a.textContent = text;
    a.target = '_blank';
    a.rel = 'noopener';
    return a;
  };
  document.querySelectorAll('time[datetime]').forEach((t) => {
    const v = videos[t.getAttribute('datetime')];
    if (!v || now < new Date(v[1])) return;
    const card = t.closest('.eps li');
    const row = t.closest('table.index tbody tr');
    const head = card ? card.querySelector('h3') : row ? row.querySelector('th') : null;
    if (!head || head.querySelector('a')) return;
    if (card) {
      const img = card.querySelector('img');
      if (!img || img.closest('a')) return;
      const a = link(v[0], '');
      a.className = 'eps__watch';
      a.setAttribute('aria-label', 'Watch ' + head.textContent + ' on YouTube (opens in a new tab)');
      img.replaceWith(a);
      const play = document.createElement('span');
      play.className = 'eps__play';
      play.setAttribute('aria-hidden', 'true');
      a.append(img, play);
      return;
    }
    const a = link(v[0], head.textContent);
    a.title = 'Opens YouTube in a new tab';
    head.textContent = '';
    head.append(a);
  });
})();
