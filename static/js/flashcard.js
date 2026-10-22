/* Flashcards: click the question to show or hide its answer. */
function toggleAnswer(btn) {
  var back = document.getElementById(btn.getAttribute('aria-controls'));
  var open = back.classList.toggle('unblur');
  btn.setAttribute('aria-expanded', open);
  back.setAttribute('aria-hidden', !open);
}
/* "Show all / Hide all" buttons:  <button class="flashcard-all" data-open="1"> */
document.addEventListener('click', function (e) {
  var b = e.target.closest('.flashcard-all'); if (!b) return;
  var open = b.dataset.open === '1', scope = b.closest('.post-content') || document;
  scope.querySelectorAll('.flashcard__front').forEach(function (f) {
    if ((f.getAttribute('aria-expanded') === 'true') !== open) toggleAnswer(f);
  });
});
