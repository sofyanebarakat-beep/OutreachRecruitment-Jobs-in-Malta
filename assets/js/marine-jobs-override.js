(function(){
  function ready(fn){
    if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  function clean(value){
    return String(value || '')
      .toLowerCase()
      .replace(/&amp;/g, '&')
      .replace(/\s+/g, ' ')
      .trim();
  }

  ready(function(){
    var path = window.location.pathname.replace(/\/$/, '');
    if(path !== '/marine-jobs-in-malta' && path !== '/marine-jobs-in-malta.html') return;

    var grid = document.querySelector('.opening-jobs-centered-grid');
    if(!grid) return;

    var jobs = [
      { title: 'Senior Purchasing Officer', url: '/jobs/purchasing-officer/', search: 'senior purchasing officer malta' },
      { title: 'Quality Engineer', url: '/jobs/quality-engineer-marine-malta/', search: 'quality engineer marine malta' },
      { title: 'QHSE Manager', url: '/jobs/qhse-manager-malta/', search: 'qhse manager malta' },
      { title: 'Purchasing Manager', url: '/jobs/purchasing-manager/', search: 'purchasing manager malta' },
      { title: 'Project Manager', url: '/jobs/project-manager/', search: 'project manager malta' },
      { title: 'Marine Turner', url: '/jobs/marine-turner-malta', search: 'marine turner malta' },
      { title: 'HSSE Coordinator', url: '/jobs/hsse-coordinator/', search: 'hsse coordinator malta' },
      { title: 'Estimator', url: '/jobs/estimator/', search: 'estimator malta' },
      { title: 'HR Administration Officer (Italian Speaker)', url: '/jobs/hr-administration-officer/', search: 'hr administration officer italian speaker malta' },
      { title: 'Crew Concierge', url: '/jobs/crew-concierge-malta/', search: 'crew concierge malta' },
      { title: 'Fleet, Tools & Facility Manager', url: 'https://outreach-recruitment-agency.careers-page.com/jobs/e23b6a72-1104-41c7-9d7e-4b96886a79f0', search: 'fleet tools facility manager malta' },
      { title: 'Marine Mechanical Foreman', url: '/jobs/marine-mechanical-foreman-malta', search: 'marine mechanical foreman malta' },
      { title: 'Plate Shop Foreman', url: '/jobs/plate-shop-foreman-malta', search: 'plate shop foreman malta' }
    ];

    function hasTitle(title){
      var wanted = clean(title);
      var headings = grid.querySelectorAll('h3, .heading-h5');
      for(var i = 0; i < headings.length; i++){
        if(clean(headings[i].textContent) === wanted) return true;
      }
      return false;
    }

    for(var i = jobs.length - 1; i >= 0; i--){
      var job = jobs[i];
      if(hasTitle(job.title)) continue;

      var card = document.createElement('article');
      card.className = 'opening-job-card opening-job-card--centered';
      card.setAttribute('data-opening-job', '');
      card.setAttribute('data-featured', 'true');
      card.setAttribute('data-latest', 'true');
      card.setAttribute('data-title', job.search);
      card.setAttribute('data-category', 'Marine');
      card.setAttribute('data-location', 'paola, malta');
      card.setAttribute('data-date', '2026-06-19');
      card.innerHTML = '<a class="opening-job-link" href="' + job.url + '"><div class="opening-card-day">New</div><img class="opening-job-logo" src="/assets/job-card-logo.jpg" alt="Outreach Recruitment job logo"><h3 class="heading-h5">' + job.title + '</h3><div class="opening-job-company">Paola, Malta</div><div class="opening-job-meta"><span>Full-Time</span><span>Marine</span></div></a>';
      grid.insertBefore(card, grid.firstChild);
    }
  });
})();
