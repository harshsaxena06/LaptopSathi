// Auto-extracted from landing-preview.html — exact content/data, ported verbatim.
import { LAPTOP_IMG } from './landingLaptopImages';

export interface LaptopEntry {
  id: string;
  name: string;
  tag: string;
  hue: string;
  img: string;
  altImg?: string;
  badge?: string;
  rating: number;
  reviews: string;
  price: string;
  mrp?: string;
  discount?: string;
  chips: string[];
  tagline: string;
  specs: Record<string, string>;
}

export const LAPTOPS: LaptopEntry[] = [
  { id:'macbook-air', name:'MSI Titan 18 HX', tag:'EXTREME PERFORMANCE', hue:'rose',
    img:LAPTOP_IMG.macbook,
    rating:4.8, reviews:'2,340', price:'₹6,00,000',
    chips:['RTX 5090','Core i9-14900HX','128GB DDR5'],
    tagline:'A no-compromise desktop-replacement built for extreme gaming and creative workloads.',
    specs:{ Processor:'Intel Core i9-14900HX', Memory:'128GB DDR5', Storage:'512GB SSD', Display:'18″ 144Hz', Graphics:'RTX 5090', Battery:'99.9Wh' } },
  { id:'rog-strix', name:'ASUS ROG Strix G16', tag:'GAMING FLAGSHIP', hue:'violet',
    img:LAPTOP_IMG.asusRogFront, badge:'New Launch',
    rating:4.7, reviews:'860', price:'₹1,89,990', mrp:'₹2,09,990', discount:'10% off',
    chips:['Core Ultra 9','RTX 5060','115W TGP'],
    tagline:'Flagship RGB gaming rig with a 115W RTX 5060 and full-day connectivity for streaming setups.',
    specs:{ Processor:'Intel Core Ultra 9 275HX', Memory:'32GB DDR5', Storage:'1TB NVMe SSD', Display:'16″ QHD+ 165Hz', Graphics:'RTX 5060 8GB', Battery:'90Wh' } },
  { id:'msi-gaming', name:'MacBook Neo', tag:'EVERYDAY & PORTABLE', hue:'blue',
    img:LAPTOP_IMG.msiOpen, badge:'Bestseller',
    rating:4.6, reviews:'2,010', price:'₹98,000',
    chips:['Liquid Retina','20h battery','Fanless'],
    tagline:'A compact, all-day companion with a vivid 13-inch Liquid Retina display.',
    specs:{ Processor:'Apple M3 (8-core)', Memory:'16GB Unified', Storage:'512GB SSD', Display:'13″ Liquid Retina', Graphics:'10-core GPU', Battery:'Up to 20 hrs' } },
  { id:'macbook-pro', name:'Apple MacBook Pro', tag:'PRO PERFORMANCE', hue:'rose',
    img:LAPTOP_IMG.macbookColors,
    rating:4.9, reviews:'1,780', price:'₹1,69,900',
    chips:['M3 Pro','22h battery','Liquid Retina XDR'],
    tagline:'Pro-grade power for video editing, dev workflows, and anything that outgrows an Air.',
    specs:{ Processor:'Apple M3 Pro (12-core)', Memory:'18GB Unified', Storage:'512GB SSD', Display:'14.2″ Liquid Retina XDR', Graphics:'18-core GPU', Battery:'Up to 22 hrs' } },
  { id:'lenovo-ideapad', name:'Lenovo IdeaPad Slim 3', tag:'BUDGET & STUDENT', hue:'blue',
    img:LAPTOP_IMG.lenovoIdeapad,
    rating:4.3, reviews:'3,150', price:'₹34,990', mrp:'₹42,990', discount:'19% off',
    chips:['Core i3 13th Gen','Dolby Audio','Backlit keys'],
    tagline:'A light, reliable daily driver for browsing, classes, and everyday office work.',
    specs:{ Processor:'Intel Core i3-1315U', Memory:'8GB DDR4', Storage:'512GB SSD', Display:'15.6″ FHD', Graphics:'Intel UHD', Battery:'Up to 8 hrs' } },
  { id:'lenovo-loq', name:'Lenovo LOQ 15', tag:'GAMING VALUE', hue:'violet', badge:'New Launch',
    img:LAPTOP_IMG.lenovoLoqFront,
    rating:4.5, reviews:'980', price:'₹89,990', mrp:'₹1,04,990', discount:'14% off',
    chips:['13th Gen i7 HX','RTX 4050','125W TDP'],
    tagline:'A 125W RTX 4050 and HX-series chip push real frame rates without a premium price.',
    specs:{ Processor:'Intel Core i7-13650HX', Memory:'16GB DDR5', Storage:'512GB SSD', Display:'15.6″ FHD 144Hz', Graphics:'RTX 4050 6GB', Battery:'60Wh' } },
  { id:'hp-15', name:'HP Laptop 15 (7000 Series)', tag:'EVERYDAY PRODUCTIVITY', hue:'amber',
    img:LAPTOP_IMG.hpLaptop,
    rating:4.4, reviews:'1,540', price:'₹54,990', mrp:'₹64,990', discount:'15% off',
    chips:['Ryzen 7','1yr Microsoft 365','Fast charge'],
    tagline:'A dependable Ryzen 7 workhorse with fast charging for busy everyday multitasking.',
    specs:{ Processor:'AMD Ryzen 7 7730U', Memory:'16GB DDR4', Storage:'512GB SSD', Display:'15.6″ FHD', Graphics:'AMD Radeon', Battery:'41Wh' } },
  { id:'hp-victus', name:'HP Victus Gaming Laptop', tag:'GAMING PERFORMANCE', hue:'accent',
    img:LAPTOP_IMG.hpVictus,
    rating:4.6, reviews:'2,470', price:'₹74,990', mrp:'₹86,990', discount:'14% off',
    chips:['144Hz display','RGB backlit','Boosted cooling'],
    tagline:'A crisp 144Hz screen and improved thermals make this a strong pick for long sessions.',
    specs:{ Processor:'AMD Ryzen 7 7840HS', Memory:'16GB DDR5', Storage:'512GB SSD', Display:'15.6″ FHD 144Hz', Graphics:'RTX 4050 6GB', Battery:'70Wh' } },
  { id:'ms-surface-laptop', name:'Microsoft Surface Laptop', tag:'PREMIUM 2-IN-1 READY', hue:'blue', badge:'New Launch',
    img:LAPTOP_IMG.msSurfaceLaptop,
    rating:4.7, reviews:'1,240', price:'₹1,29,999', mrp:'₹1,44,999', discount:'10% off',
    chips:['Snapdragon X','Copilot+ PC','120Hz touch'],
    tagline:'A fanless Copilot+ PC with a vivid touch display and all-day battery for life on the move.',
    specs:{ Processor:'Snapdragon X Elite', Memory:'16GB Unified', Storage:'512GB SSD', Display:'13.8″ PixelSense 120Hz', Graphics:'Adreno GPU', Battery:'Up to 20 hrs' } },
  { id:'macbook-air-silver', name:'Apple MacBook Air (Silver)', tag:'EVERYDAY & PORTABLE', hue:'rose',
    img:LAPTOP_IMG.macbookAirRear,
    rating:4.8, reviews:'3,020', price:'₹99,900', mrp:'₹1,14,900', discount:'13% off',
    chips:['M2 chip','18h battery','Fanless'],
    tagline:'The classic silver Air — ultra-thin, whisper-quiet, and light enough to carry anywhere.',
    specs:{ Processor:'Apple M2 (8-core)', Memory:'8GB Unified', Storage:'256GB SSD', Display:'13.3″ Retina', Graphics:'Apple Silicon Integrated GPU', Battery:'Up to 18 hrs' } },
];

export interface FeatureEntry { icon: string; hue: string; title: string; desc: string; }
export const FEATURES: FeatureEntry[] = [
  { icon:'sparkle', hue:'accent', title:'AI-Powered Recommendations', desc:'Get laptop recommendations based on your actual needs, preferences, and budget instead of generic lists.' },
  { icon:'search', hue:'blue', title:'Semantic Search', desc:'Search naturally for what you need and let LaptopSathi understand the intent behind your query.' },
  { icon:'wallet', hue:'amber', title:'Budget Optimization', desc:'Find the best-performing options within your budget and understand where your money delivers the most value.' },
  { icon:'bulb', hue:'violet', title:'Explainable AI', desc:'Understand why a laptop was recommended instead of receiving a mysterious AI-generated answer.' },
  { icon:'compare', hue:'rose', title:'Hardware Comparison', desc:'Compare processors, GPUs, RAM, storage, displays, battery life, and other important specifications side by side.' },
  { icon:'sliders', hue:'accent', title:'Personalized Suggestions', desc:'Get recommendations tailored to your use case — gaming, coding, college, productivity, content creation, or everyday use.' },
];

export interface StepEntry { n: string; title: string; desc: string; }
export const STEPS: StepEntry[] = [
  { n:'01', title:'Tell us what you need', desc:'Describe your budget, workload, preferences, and priorities.' },
  { n:'02', title:'LaptopSathi understands', desc:'Our AI analyzes your requirements against laptop specifications and product knowledge.' },
  { n:'03', title:'Compare your options', desc:'Explore relevant laptops and understand their strengths, weaknesses, and trade-offs.' },
  { n:'04', title:'Make your decision', desc:'Choose with confidence based on recommendations you can actually understand.' },
];

export interface ValueEntry { icon: string; hue: string; title: string; desc: string; }
export const VALUES: ValueEntry[] = [
  { icon:'db', hue:'accent', title:'Real Knowledge Base', desc:'Recommendations grounded in structured laptop and hardware information.' },
  { icon:'bulb', hue:'amber', title:'Explainable Recommendations', desc:'Understand the reasoning behind your recommendations.' },
  { icon:'gauge', hue:'blue', title:'Decision Focused', desc:'Less information overload. More clarity.' },
];
