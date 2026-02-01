'use client';

import Link from 'next/link';
import { ArrowRight, Sparkles, Video, Image, Wand2, Globe, Zap, Shield } from 'lucide-react';

export default function LandingPage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
            {/* Navigation */}
            <nav className="fixed top-0 left-0 right-0 z-50 bg-gray-900/80 backdrop-blur-xl border-b border-gray-700/50">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <span className="text-3xl">🫑</span>
                        <span className="text-xl font-bold text-white">Pepper Root</span>
                    </div>
                    <div className="flex items-center gap-4">
                        <Link
                            href="/login"
                            className="text-gray-300 hover:text-white transition-colors"
                        >
                            Giriş Yap
                        </Link>
                        <Link
                            href="/login"
                            className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded-lg font-medium transition-all hover:scale-105"
                        >
                            Ücretsiz Başla
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="pt-32 pb-20 px-6">
                <div className="max-w-6xl mx-auto text-center">
                    {/* Badge */}
                    <div className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-4 py-2 rounded-full text-sm mb-8">
                        <Sparkles size={16} />
                        AI ile Görsel ve Video Üretimi
                    </div>

                    {/* Main Title */}
                    <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
                        Yaratıcılığınızı
                        <br />
                        <span className="bg-gradient-to-r from-emerald-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent">
                            Sınırsız Yapın
                        </span>
                    </h1>

                    {/* Subtitle */}
                    <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10">
                        Karakterler oluşturun, mekanlar tasarlayın, görseller üretin ve
                        AI destekli asistanınızla profesyonel videolar oluşturun.
                    </p>

                    {/* CTA Buttons */}
                    <div className="flex items-center justify-center gap-4 mb-16">
                        <Link
                            href="/login"
                            className="group inline-flex items-center gap-3 bg-emerald-600 hover:bg-emerald-700 text-white px-8 py-4 rounded-xl font-medium text-lg transition-all hover:scale-105 shadow-lg shadow-emerald-500/25"
                        >
                            Hemen Başla
                            <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                        </Link>
                        <a
                            href="#features"
                            className="inline-flex items-center gap-2 text-gray-400 hover:text-white px-6 py-4 transition-colors"
                        >
                            Özellikleri Keşfet
                        </a>
                    </div>

                    {/* Hero Image/Preview */}
                    <div className="relative max-w-5xl mx-auto">
                        <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-transparent to-transparent z-10"></div>
                        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-4 shadow-2xl">
                            <div className="bg-gray-900 rounded-xl p-6 min-h-[400px] flex items-center justify-center">
                                <div className="text-center">
                                    <div className="text-6xl mb-4">🎬</div>
                                    <p className="text-gray-500">AI Studio Önizleme</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="py-20 px-6 bg-gray-800/30">
                <div className="max-w-6xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                            Her Şey Tek Platformda
                        </h2>
                        <p className="text-gray-400 max-w-xl mx-auto">
                            Profesyonel içerik üretimi için ihtiyacınız olan tüm araçlar
                        </p>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {/* Feature 1 */}
                        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-6 border border-gray-700/50 hover:border-emerald-500/50 transition-colors group">
                            <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Image size={24} className="text-emerald-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">Görsel Üretimi</h3>
                            <p className="text-gray-400">
                                AI ile yüksek kaliteli görseller oluşturun. Karakterler, ürünler, sahneler...
                            </p>
                        </div>

                        {/* Feature 2 */}
                        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-6 border border-gray-700/50 hover:border-cyan-500/50 transition-colors group">
                            <div className="w-12 h-12 bg-cyan-500/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Video size={24} className="text-cyan-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">Video Oluşturma</h3>
                            <p className="text-gray-400">
                                Görsellerinizi profesyonel videolara dönüştürün. Tek tıkla animasyon.
                            </p>
                        </div>

                        {/* Feature 3 */}
                        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-6 border border-gray-700/50 hover:border-purple-500/50 transition-colors group">
                            <div className="w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Wand2 size={24} className="text-purple-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">Akıllı Düzenleme</h3>
                            <p className="text-gray-400">
                                Arka plan değiştirme, upscale, yüz değiştirme ve daha fazlası.
                            </p>
                        </div>

                        {/* Feature 4 */}
                        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-6 border border-gray-700/50 hover:border-orange-500/50 transition-colors group">
                            <div className="w-12 h-12 bg-orange-500/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Globe size={24} className="text-orange-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">Web Entegrasyonu</h3>
                            <p className="text-gray-400">
                                İnternetten görsel ve bilgi arayın. Marka görselleri otomatik bulunur.
                            </p>
                        </div>

                        {/* Feature 5 */}
                        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-6 border border-gray-700/50 hover:border-yellow-500/50 transition-colors group">
                            <div className="w-12 h-12 bg-yellow-500/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Zap size={24} className="text-yellow-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">Hızlı Üretim</h3>
                            <p className="text-gray-400">
                                Saniyeler içinde profesyonel sonuçlar. 25+ AI modeli entegre.
                            </p>
                        </div>

                        {/* Feature 6 */}
                        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-6 border border-gray-700/50 hover:border-pink-500/50 transition-colors group">
                            <div className="w-12 h-12 bg-pink-500/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Shield size={24} className="text-pink-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">Güvenli Depolama</h3>
                            <p className="text-gray-400">
                                Tüm üretimleriniz güvenle saklanır. İstediğiniz zaman erişin.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-20 px-6">
                <div className="max-w-4xl mx-auto text-center">
                    <div className="bg-gradient-to-br from-emerald-600/20 to-purple-600/20 rounded-3xl p-12 border border-gray-700/50">
                        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                            Yaratmaya Hazır mısınız?
                        </h2>
                        <p className="text-gray-400 mb-8 max-w-xl mx-auto">
                            Ücretsiz hesap oluşturun ve AI destekli içerik üretimine hemen başlayın.
                        </p>
                        <Link
                            href="/login"
                            className="inline-flex items-center gap-3 bg-white text-gray-900 px-8 py-4 rounded-xl font-medium text-lg transition-all hover:scale-105 shadow-lg"
                        >
                            <span className="text-2xl">🫑</span>
                            Ücretsiz Başla
                            <ArrowRight size={20} />
                        </Link>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-8 px-6 border-t border-gray-800">
                <div className="max-w-6xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <span className="text-xl">🫑</span>
                        <span className="text-gray-500">Pepper Root AI Agency</span>
                    </div>
                    <p className="text-gray-500 text-sm">
                        © 2026 Tüm hakları saklıdır.
                    </p>
                </div>
            </footer>
        </div>
    );
}
