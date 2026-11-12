// Магазин и сохранения
window.Shop = {
  coins: parseInt(localStorage.getItem('flappyCoins') || '0', 10),
  currentSkin: localStorage.getItem('flappySkin') || 'classic',
  
  skins: {
    classic: { name: 'Классика', price: 0, color: '#f7d51d', eye: '#fff' },
    red: { name: 'Красная', price: 10, color: '#ff4d4d', eye: '#fff' },
    penguin: { name: 'Пингвин', price: 25, color: '#2d2d2d', eye: '#fff' },
    golden: { name: 'Золотая', price: 50, color: '#ffd700', eye: '#fff' },
  },

  addCoin: function() {
    this.coins++;
    localStorage.setItem('flappyCoins', this.coins);
  },

  buySkin: function(id) {
    const skin = this.skins[id];
    if (this.coins >= skin.price && this.currentSkin !== id) {
      this.coins -= skin.price;
      this.currentSkin = id;
      localStorage.setItem('flappyCoins', this.coins);
      localStorage.setItem('flappySkin', id);
      return true;
    }
    return false;
  }
};