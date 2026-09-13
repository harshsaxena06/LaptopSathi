import React from 'react';
import { SimplePageChrome } from '@/components/landing/SimplePageChrome';

export function PrivacyPage() {
  return (
    <SimplePageChrome>
      <div className="legal-page">
        <div className="section-head reveal" style={{ textAlign: 'left', margin: '0 0 8px' }}>
          <span className="section-eyebrow">Legal</span>
          <h2 style={{ marginBottom: 0 }}>Privacy Policy</h2>
        </div>
        <p className="legal-meta">Last updated: September 2026</p>

        <div className="legal-section reveal">
          <h3>1. What we collect</h3>
          <ul className="legal-list">
            <li>Account details you provide directly — name, email address, and password (stored hashed, never in plain text).</li>
            <li>Usage data such as searches, comparisons, and saved laptops, so recommendations can be personalized.</li>
            <li>Basic technical data (device/browser type, approximate region) used for security and debugging.</li>
          </ul>
        </div>

        <div className="legal-section reveal">
          <h3>2. What we don&apos;t do</h3>
          <ul className="legal-list">
            <li>We don&apos;t sell your personal data to advertisers or data brokers.</li>
            <li>We don&apos;t run third-party ad trackers on this site.</li>
            <li>We don&apos;t share your account data with laptop manufacturers or retailers.</li>
          </ul>
        </div>

        <div className="legal-section reveal">
          <h3>3. How your data is used</h3>
          <ul className="legal-list">
            <li>To generate and improve laptop recommendations tailored to your preferences and budget.</li>
            <li>To keep your account secure — for example, detecting unusual sign-in activity.</li>
            <li>To understand, in aggregate, which features are actually useful so the product can improve.</li>
          </ul>
        </div>

        <div className="legal-section reveal">
          <h3>4. Your choices</h3>
          <ul className="legal-list">
            <li>You can review and update your account details at any time from your profile.</li>
            <li>You can request a copy of your data or full account deletion whenever you&apos;d like.</li>
            <li>You can stop using the service at any time — no dark patterns, no retention tricks.</li>
          </ul>
        </div>

        <div className="legal-section reveal">
          <h3>5. Contact</h3>
          <p>
            For any privacy questions or data requests, reach out to the project maintainer,
            Harsh, through the contact details on the About page.
          </p>
        </div>
      </div>
    </SimplePageChrome>
  );
}
